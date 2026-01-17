export interface SearchMatch {
  file: string;
  start: number;
  end: number;
  content: string;
  score?: number;
}

export interface VideoFile {
  id?: number;
  path: string;
  filename: string;
  size_bytes: number;
  duration: number;
  created_at: number;
  has_transcript: boolean;
  transcript_path?: string;
}

export interface NGramMatch {
  ngram: string;
  count: number;
}

export type AppStatus = "idle" | "downloading" | "transcribing" | "exporting" | "error";