export interface AIClassification {
  id_hang_muc: string | null;
  ten_hang_muc: string | null;
  nhom_hoa_chat: string | null;
  ghi_chu_ai: string | null;
}

export interface LegalEntry {
  chuong: string;
  muc: string;
  tieu_de_muc: string;
  dieu: string;
  tieu_de_dieu: string;
  khoan: string;
  diem: string;
  noi_dung: string;
  ai_classification: AIClassification;
}

export interface LegalData {
  metadata: {
    export_time: string;
    total_entries: number;
    format: string;
    definitions: any;
  };
  data: LegalEntry[];
}
