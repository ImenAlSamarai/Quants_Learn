import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Node APIs
export const fetchMindMap = async (category = null) => {
  const params = category ? { category } : {};
  const response = await api.get('/api/nodes/mindmap', { params });
  return response.data;
};

export const fetchNode = async (nodeId) => {
  const response = await api.get(`/api/nodes/${nodeId}`);
  return response.data;
};

export const fetchNodesByCategory = async (category) => {
  const response = await api.get(`/api/nodes/category/${category}`);
  return response.data;
};

// Content APIs
export const queryContent = async (nodeId, queryType, userContext = null) => {
  const response = await api.post('/api/content/query', {
    node_id: nodeId,
    query_type: queryType,
    user_context: userContext,
  });
  return response.data;
};

export const getNodeSummary = async (nodeId) => {
  const response = await api.get(`/api/content/node/${nodeId}/summary`);
  return response.data;
};

export const searchContent = async (query, category = null, topK = 10) => {
  const params = { query, top_k: topK };
  if (category) params.category = category;
  const response = await api.get('/api/content/search', { params });
  return response.data;
};

// Progress APIs
export const fetchUserProgress = async (userId) => {
  const response = await api.get(`/api/progress/user/${userId}`);
  return response.data;
};

export const updateProgress = async (userId, nodeId, completed, quizScore = null, timeSpent = 0) => {
  const response = await api.post('/api/progress/update', {
    user_id: userId,
    node_id: nodeId,
    completed,
    quiz_score: quizScore,
    time_spent_minutes: timeSpent,
  });
  return response.data;
};

export const getRecommendations = async (userId) => {
  const response = await api.get(`/api/progress/user/${userId}/recommendations`);
  return response.data;
};

export default api;
