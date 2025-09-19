import axios from 'axios';

// API Gateway URL
const API_GATEWAY_URL = 'http://localhost:5000/api';

// Multimedia Service URL
const MULTIMEDIA_SERVICE_URL = process.env.REACT_APP_MULTIMEDIA_SERVICE_URL || 'http://localhost:8001';

const apiClient = axios.create({
  baseURL: API_GATEWAY_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const multimediaClient = axios.create({
  baseURL: MULTIMEDIA_SERVICE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const createCurriculum = (topic) => {
  return apiClient.post('/create-curriculum', { topic });
};

export const createAssessment = (content, assessment_type) => {
  return apiClient.post('/create-assessment', { content, assessment_type });
};

export const personalizeContent = (topic, user_id, user_role = 'employee') => {
  return apiClient.post('/personalize-content', { topic, user_id, user_role });
};


export const summarizeText = (text, format_type, length) => {
  return apiClient.post('/summarize-text', { text, format_type, length });
};

export const generateImage = (prompt, image_type = 'general') => {
  return multimediaClient.post('/generate-image', { prompt, image_type });
};

export const localizeText = (text, target_language, glossary, localize) => {
  return apiClient.post('/localize-text', { text, target_language, glossary, localize });
};
