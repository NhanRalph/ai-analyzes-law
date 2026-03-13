"use client";

import React, { useMemo, useState, useEffect } from 'react';
import { LegalEntry } from '@/types/legal';
import { ResultCard } from '@/components/ResultCard';
import dataFile from '@/data/legal_data.json';

const legalData = dataFile as any;

export default function Home() {
  const [selectedChuong, setSelectedChuong] = useState<string>('');
  const [selectedDieu, setSelectedDieu] = useState<string>('');
  const [selectedKhoan, setSelectedKhoan] = useState<string>('');
  const [selectedHangMuc, setSelectedHangMuc] = useState<string[]>([]);
  const [selectedNhom, setSelectedNhom] = useState<string[]>([]);
  const [openFilter, setOpenFilter] = useState<string | null>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (!(event.target as HTMLElement).closest('.multi-select-wrapper')) {
        setOpenFilter(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const toggleFilter = (list: string[], setList: (v: string[]) => void, value: string) => {
    if (list.includes(value)) {
      setList(list.filter(v => v !== value));
    } else {
      setList([...list, value]);
    }
  };

  const entries: LegalEntry[] = legalData.data;

  // Extract unique options
  const chuongOptions = useMemo(() => 
    Array.from(new Set(entries.map(e => e.chuong).filter(Boolean))),
    [entries]
  );

  const dieuOptions = useMemo(() => {
    let filtered = entries;
    if (selectedChuong) filtered = filtered.filter(e => e.chuong === selectedChuong);
    return Array.from(new Set(filtered.map(e => e.dieu).filter(Boolean)));
  }, [entries, selectedChuong]);

  const khoanOptions = useMemo(() => {
    if (!selectedDieu) return [];
    let filtered = entries.filter(e => e.dieu === selectedDieu);
    if (selectedChuong) filtered = filtered.filter(e => e.chuong === selectedChuong);
    return Array.from(new Set(filtered.map(e => e.khoan).filter(Boolean)));
  }, [entries, selectedDieu, selectedChuong]);

  const hangMucOptions = useMemo(() => 
    Array.from(new Set(entries.map(e => e.ai_classification.ten_hang_muc).filter(Boolean))),
    [entries]
  );

  const nhomOptions = useMemo(() => 
    Array.from(new Set(entries.map(e => e.ai_classification.nhom_hoa_chat).filter(Boolean))),
    [entries]
  );

  // Filtered results
  const filteredEntries = useMemo(() => {
    return entries.filter(e => {
      if (selectedChuong && e.chuong !== selectedChuong) return false;
      if (selectedDieu && e.dieu !== selectedDieu) return false;
      if (selectedKhoan && e.khoan !== selectedKhoan) return false;
      
      // Multi-select filters
      if (selectedHangMuc.length > 0 && !selectedHangMuc.includes(e.ai_classification.ten_hang_muc || '')) return false;
      if (selectedNhom.length > 0 && !selectedNhom.includes(e.ai_classification.nhom_hoa_chat || '')) return false;
      
      return true;
    });
  }, [entries, selectedChuong, selectedDieu, selectedKhoan, selectedHangMuc, selectedNhom]);

  return (
    <main className="container">
      <header className="header">
        <h1 className="title">Legal Data Viewer</h1>
        <p className="subtitle">Tra cứu dữ liệu pháp luật về hóa chất</p>
      </header>

      <div className="filter-grid">
        <div className="form-group">
          <label className="label">Chương</label>
          <select 
            className="select" 
            value={selectedChuong} 
            onChange={(e) => {
              setSelectedChuong(e.target.value);
              setSelectedDieu('');
              setSelectedKhoan('');
            }}
          >
            <option value="">Tất cả</option>
            {chuongOptions.map(opt => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label className="label">Điều</label>
          <select 
            className="select" 
            value={selectedDieu} 
            onChange={(e) => {
              setSelectedDieu(e.target.value);
              setSelectedKhoan('');
            }}
          >
            <option value="">Tất cả</option>
            {dieuOptions.map(opt => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label className="label">Khoản</label>
          <select 
            className="select" 
            value={selectedKhoan} 
            onChange={(e) => setSelectedKhoan(e.target.value)}
            disabled={!selectedDieu}
          >
            <option value="">Tất cả</option>
            {khoanOptions.map(opt => (
              <option key={opt} value={opt}>Khoản {opt}</option>
            ))}
          </select>
        </div>

        <div className="form-group multi-select-wrapper">
          <label className="label">Hạng mục (AI)</label>
          <button 
            className={`select dropdown-toggle ${openFilter === 'hang_muc' ? 'active' : ''}`}
            onClick={() => setOpenFilter(openFilter === 'hang_muc' ? null : 'hang_muc')}
            type="button"
          >
            {selectedHangMuc.length > 0 
              ? `${selectedHangMuc.length} đã chọn` 
              : 'Chọn hạng mục...'}
            <span className="chevron">▼</span>
          </button>
          
          {openFilter === 'hang_muc' && (
            <div className="dropdown-content animate-in">
              <div className="checkbox-group">
                {hangMucOptions.map(opt => (
                  <label key={opt || 'none'} className="checkbox-item">
                    <input 
                      type="checkbox" 
                      checked={selectedHangMuc.includes(opt || '')}
                      onChange={() => toggleFilter(selectedHangMuc, setSelectedHangMuc, opt || '')}
                    />
                    <span className="checkbox-label">{opt || 'Không xác định'}</span>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="form-group multi-select-wrapper">
          <label className="label">Nhóm hóa chất (AI)</label>
          <button 
            className={`select dropdown-toggle ${openFilter === 'nhom' ? 'active' : ''}`}
            onClick={() => setOpenFilter(openFilter === 'nhom' ? null : 'nhom')}
            type="button"
          >
            {selectedNhom.length > 0 
              ? `${selectedNhom.length} đã chọn` 
              : 'Chọn nhóm...'}
            <span className="chevron">▼</span>
          </button>

          {openFilter === 'nhom' && (
            <div className="dropdown-content animate-in">
              <div className="checkbox-group">
                {nhomOptions.map(opt => (
                  <label key={opt || 'none'} className="checkbox-item">
                    <input 
                      type="checkbox" 
                      checked={selectedNhom.includes(opt || '')}
                      onChange={() => toggleFilter(selectedNhom, setSelectedNhom, opt || '')}
                    />
                    <span className="checkbox-label">{opt || 'Không xác định'}</span>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="results-grid">
        <div style={{ marginBottom: '1rem', color: '--secondary', fontSize: '0.9rem' }}>
          Tìm thấy <strong>{filteredEntries.length}</strong> kết quả
        </div>
        {filteredEntries.length > 0 ? (
          filteredEntries.map((entry, idx) => (
            <ResultCard key={idx} entry={entry} index={idx} />
          ))
        ) : (
          <div className="card" style={{ textAlign: 'center', padding: '4rem' }}>
            <p style={{ color: 'var(--secondary)' }}>Không tìm thấy kết quả phù hợp với bộ lọc.</p>
          </div>
        )}
      </div>
    </main>
  );
}
