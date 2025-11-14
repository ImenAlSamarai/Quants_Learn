import { create } from 'zustand';

const useAppStore = create((set, get) => ({
      // Navigation state
      currentCategory: null,
      currentTopic: null,
      viewMode: 'study', // 'study' or 'explore'

      // UI state
      sidebarCollapsed: false,

      // User progress
      completedTopics: [],
      currentProgress: {},

      // Data
      categories: [],
      topics: [],

      // Actions
      setCurrentCategory: (categoryId) => set({ currentCategory: categoryId }),

      setCurrentTopic: (topicId) => set({ currentTopic: topicId }),

      setViewMode: (mode) => set({ viewMode: mode }),

      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),

      markTopicComplete: (topicId) => set((state) => {
        if (!state.completedTopics.includes(topicId)) {
          return { completedTopics: [...state.completedTopics, topicId] };
        }
        return state;
      }),

      setCategories: (categories) => set({ categories }),

      setTopics: (topics) => set({ topics }),

      updateProgress: (categoryId, progress) => set((state) => ({
        currentProgress: {
          ...state.currentProgress,
          [categoryId]: progress,
        },
      })),

      // Getters
      getCategoryProgress: (categoryId) => {
        const state = get();
        const categoryTopics = state.topics.filter(
          (topic) => topic.category === categoryId
        );
        const completedCount = categoryTopics.filter((topic) =>
          state.completedTopics.includes(topic.id)
        ).length;
        return {
          total: categoryTopics.length,
          completed: completedCount,
          percentage: categoryTopics.length > 0
            ? Math.round((completedCount / categoryTopics.length) * 100)
            : 0,
        };
      },

      getRelatedTopics: (topicId) => {
        const state = get();
        const currentTopic = state.topics.find((t) => t.id === topicId);
        if (!currentTopic) return [];

        return state.topics.filter((topic) =>
          topic.id !== topicId &&
          (topic.prerequisites?.includes(topicId) ||
           currentTopic.prerequisites?.includes(topic.id) ||
           topic.category === currentTopic.category)
        );
      },

      reset: () => set({
        currentCategory: null,
        currentTopic: null,
        viewMode: 'study',
        sidebarCollapsed: false,
      }),
    }));

export default useAppStore;
