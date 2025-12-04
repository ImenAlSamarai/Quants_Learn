import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 600000, // 10 minute timeout (learning path generation with RAG + LLM can take 2-5 minutes for large job descriptions)
});

// Demo data for when backend is unavailable
const generateDemoData = (category) => {
  const demoNodes = {
    linear_algebra: [
      { id: 1, title: 'Vectors and Spaces', description: 'Understand vector fundamentals', difficulty_level: 1, parent_ids: [], icon: '📐' },
      { id: 2, title: 'Matrix Operations', description: 'Learn matrix multiplication and properties', difficulty_level: 2, parent_ids: [1], icon: '🔢' },
      { id: 3, title: 'Linear Transformations', description: 'Map vectors to vectors linearly', difficulty_level: 3, parent_ids: [2], icon: '↔️' },
      { id: 4, title: 'Eigenvalues & Eigenvectors', description: 'Special vectors and scaling factors', difficulty_level: 4, parent_ids: [2, 3], icon: '⚡' },
    ],
    calculus: [
      { id: 11, title: 'Limits', description: 'Foundation of calculus', difficulty_level: 1, parent_ids: [], icon: '∞' },
      { id: 12, title: 'Derivatives', description: 'Rate of change', difficulty_level: 2, parent_ids: [11], icon: '📈' },
      { id: 13, title: 'Integrals', description: 'Area under curves', difficulty_level: 3, parent_ids: [12], icon: '∫' },
      { id: 14, title: 'Optimization', description: 'Find extrema', difficulty_level: 4, parent_ids: [12], icon: '🎯' },
    ],
    probability: [
      { id: 21, title: 'Sample Spaces', description: 'Possible outcomes', difficulty_level: 1, parent_ids: [], icon: '🎲' },
      { id: 22, title: 'Random Variables', description: 'Numerical outcomes', difficulty_level: 2, parent_ids: [21], icon: '🔀' },
      { id: 23, title: 'Distributions', description: 'Probability patterns', difficulty_level: 3, parent_ids: [22], icon: '📊' },
      { id: 24, title: 'Expectation', description: 'Average values', difficulty_level: 3, parent_ids: [22], icon: '⭐' },
    ],
    statistics: [
      { id: 31, title: 'Descriptive Stats', description: 'Summarize data', difficulty_level: 1, parent_ids: [], icon: '📊' },
      { id: 32, title: 'Hypothesis Testing', description: 'Test claims', difficulty_level: 2, parent_ids: [31], icon: '🧪' },
      { id: 33, title: 'Regression', description: 'Model relationships', difficulty_level: 3, parent_ids: [31], icon: '📉' },
      { id: 34, title: 'Time Series', description: 'Temporal patterns', difficulty_level: 4, parent_ids: [33], icon: '⏱️' },
    ],
  };

  return {
    nodes: demoNodes[category] || [],
    edges: demoNodes[category]?.map(node =>
      node.parent_ids.map(parentId => ({ parent_id: parentId, child_id: node.id }))
    ).flat() || [],
  };
};

// Node APIs
export const fetchMindMap = async (category = null) => {
  try {
    const params = category ? { category } : {};
    const response = await api.get('/api/nodes/mindmap', { params });
    return response.data;
  } catch (error) {
    console.warn('Backend unavailable, using demo data:', error.message);
    return generateDemoData(category);
  }
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
export const queryContent = async (nodeId, queryType = 'explanation', userContext = null, userId = 'demo_user') => {
  console.log('🔵 [API] queryContent called:', { nodeId, queryType, userId });

  try {
    const requestData = {
      node_id: nodeId,
      query_type: queryType,
      user_id: userId,
      user_context: userContext,
      force_regenerate: false,
    };

    console.log('🔵 [API] Sending request to backend:', requestData);

    const response = await api.post('/api/content/query', requestData);

    console.log('✅ [API] Response received:', {
      nodeTitle: response.data.node_title,
      contentType: response.data.content_type,
      hasContent: !!response.data.generated_content,
      contentLength: response.data.generated_content?.length,
      contentPreview: response.data.generated_content?.substring(0, 100),
    });

    return response.data;
  } catch (error) {
    console.error('❌ [API] Error fetching content:', error);
    console.error('❌ [API] Error details:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
    });
    throw error;
  }
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

// Phase 2: Progress Dashboard APIs
export const getUserDashboard = async (userId) => {
  const response = await api.get(`/api/users/${userId}/dashboard`);
  return response.data;
};

export const updateUserProfile = async (userId, profileData) => {
  const response = await api.patch(`/api/users/${userId}/profile`, profileData);
  return response.data;
};

export const logStudySession = async (userId, nodeId, durationSeconds) => {
  const response = await api.post('/api/progress/session', {
    user_id: userId,
    node_id: nodeId,
    duration_seconds: durationSeconds,
  });
  return response.data;
};

// Phase 2.5: Job-Based Personalization APIs
export const updateJobProfile = async (userId, jobData) => {
  const response = await api.post(`/api/users/${userId}/job-profile`, jobData);
  return response.data;
};

export const getLearningPath = async (userId) => {
  const response = await api.get(`/api/users/${userId}/learning-path`);
  return response.data;
};

export const checkTopicCoverage = async (topic) => {
  const response = await api.post('/api/users/check-coverage', { topic });
  return response.data;
};

export const getSectionContent = async (topicName, sectionId, sectionTitle, keywords = []) => {
  const params = {
    section_title: sectionTitle,
    keywords: keywords.join(',')
  };

  const response = await api.get(
    `/api/users/topics/${encodeURIComponent(topicName)}/sections/${sectionId}/content`,
    { params }
  );

  return response.data;
};

export default api;
