import axios from "axios";
import { VideoFile, SearchMatch, NGramMatch } from "./types";

const API_BASE_URL = "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const getLibrary = async (): Promise<VideoFile[]> => {
  const { data } = await api.get("/library");
  return data;
};

export const scanLibrary = async (path: string): Promise<{ added: number }> => {
  const { data } = await api.post(`/library/scan?path=${encodeURIComponent(path)}`);
  return data;
};

export const searchMedia = async (
  query: string,
  type: string,
  threshold: number
): Promise<SearchMatch[]> => {
  const { data } = await api.get("/search", {
    params: { query, type, threshold },
  });
  return data;
};

export const downloadVideo = async (url: string): Promise<any> => {
  const { data } = await api.post(`/download?url=${encodeURIComponent(url)}`);
  return data;
};

export const getNGrams = async (path: string, n: number): Promise<NGramMatch[]> => {
  const { data } = await api.get("/ngrams", {
    params: { path, n },
  });
  return data;
};

export const exportSupercut = async (
  matches: SearchMatch[],
  output: string
): Promise<{ status: string; path: string }> => {
  const { data } = await api.post("/export", matches, {
    params: { output },
  });
  return data;
};

export const openFolder = async (path: string): Promise<{ status: string }> => {
  const { data } = await api.post("/open_folder", null, {
    params: { path },
  });
  return data;
};
