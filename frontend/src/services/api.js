import axios from 'axios';

// All requests go to the API Gateway running on localhost:5000
const API_GATEWAY_URL = 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: API_GATEWAY_URL,
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

export const generateImage = (prompt) => {
  return apiClient.post('/generate-image', { prompt });
};

export const localizeText = (text, target_language, glossary, localize) => {
  return apiClient.post('/localize-text', { text, target_language, glossary, localize });
};
