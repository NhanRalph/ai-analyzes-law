import React from 'react';
import { LegalEntry } from '@/types/legal';

interface ResultCardProps {
  entry: LegalEntry;
  index: number;
}

export const ResultCard: React.FC<ResultCardProps> = ({ entry, index }) => {
  return (
    <div className="card animate-in" style={{ animationDelay: `${index * 0.05}s` }}>
      <div className="card-header">
        <h3 className="card-title">
          {entry.dieu} {entry.tieu_de_dieu && `: ${entry.tieu_de_dieu}`}
        </h3>
        <div className="card-meta">
          {[entry.chuong, entry.khoan && `Khoản ${entry.khoan}`, entry.diem && `Điểm ${entry.diem}`]
            .filter(Boolean)
            .join(' • ')}
        </div>
      </div>

      <div className="card-content">
        {entry.noi_dung}
      </div>

      {(entry.ai_classification.ghi_chu_ai || entry.ai_classification.ten_hang_muc) && (
        <div className="ai-section">
          <div className="ai-header">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a10 10 0 1 0 10 10H12V2z" />
              <path d="M12 12L2.1 12.1" />
              <path d="M12 12V22" />
              <path d="M12 12L21.9 11.9" />
            </svg>
            AI Insight
          </div>
          {entry.ai_classification.ghi_chu_ai && (
            <p className="ai-notes">{entry.ai_classification.ghi_chu_ai}</p>
          )}
          <div className="tag-list">
            {entry.ai_classification.ten_hang_muc && (
              <span className="tag">{entry.ai_classification.ten_hang_muc}</span>
            )}
            {entry.ai_classification.nhom_hoa_chat && (
              <span className="tag">Nhóm: {entry.ai_classification.nhom_hoa_chat}</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
