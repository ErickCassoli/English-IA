export interface PracticeTopic {
    code: string;
    label: string;
    description: string;
}

export interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    text: string;
    detected_errors?: DetectedError[];
}

export interface DetectedError {
    start: number;
    end: number;
    category: string;
    user_text: string;
    corrected_text: string;
    note: string;
}

export interface SessionResponse {
    session_id: string;
    topic_code: string;
    topic_label: string;
    topic_description: string;
    system_prompt: string;
    status: string;
    started_at: string;
    ended_at: string | null;
    active_minutes: number;
    last_interaction_at: string;
}

export interface Settings {
    llm_provider: string;
    llm_model: string;
    native_language?: string;
    target_language?: string;
}

export interface DashboardSummary {
    study_time_hours: number;
    study_time_total_seconds: number;
    words_learned: number;
    conversations: number;
    fluency_level: string;
    fluency_score: number;
    is_assessed: boolean;
    skills: {
        reading: number;
        writing: number;
        listening: number;
        speaking: number;
    };
    due_flashcards: number;
    minutes_today: number;
    current_streak_days: number;
    longest_streak_days: number;
    last_practice_date: string | null;
}

const API_URL = '/api';

export const api = {
    getTopics: async (): Promise<PracticeTopic[]> => {
        const res = await fetch(`${API_URL}/practice/topics`);
        if (!res.ok) throw new Error('Failed to fetch topics');
        return res.json();
    },

    createSession: async (topicCode?: string | null, customTopic?: string): Promise<SessionResponse> => {
        const body: any = {};
        if (topicCode) body.topic_code = topicCode;
        if (customTopic) body.custom_topic = customTopic;

        const res = await fetch(`${API_URL}/sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error('Failed to create session');
        return res.json();
    },

    getHistory: async (sessionId: string): Promise<ChatMessage[]> => {
        const res = await fetch(`${API_URL}/chat/${sessionId}/history`);
        if (!res.ok) throw new Error('Failed to fetch history');
        return res.json();
    },

    sendMessage: async (sessionId: string, text: string): Promise<{ reply: string, detected_errors: any[] }> => {
        const res = await fetch(`${API_URL}/chat/${sessionId}/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text }),
        });
        if (!res.ok) throw new Error('Failed to send message');
        return res.json();
    },

    finishSession: async (sessionId: string): Promise<{ quizzes: any[], flashcards: any[] }> => {
        const res = await fetch(`${API_URL}/sessions/${sessionId}/finish`, {
            method: 'POST',
        });
        if (!res.ok) throw new Error('Failed to finish session');
        return res.json();
    },

    getDueFlashcards: async (): Promise<any[]> => {
        const res = await fetch(`${API_URL}/flashcards/due`);
        if (!res.ok) throw new Error('Failed to fetch flashcards');
        return res.json();
    },

    createFlashcard: async (front: string, back: string): Promise<any> => {
        const res = await fetch(`${API_URL}/flashcards/manual`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ front, back }),
        });
        if (!res.ok) throw new Error('Failed to create flashcard');
        return res.json();
    },

    reviewFlashcard: async (cardId: string, quality: number): Promise<any> => {
        const res = await fetch(`${API_URL}/flashcards/${cardId}/review`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quality }),
        });
        if (!res.ok) throw new Error('Failed to review flashcard');
        return res.json();
    },

    getSettings: async (): Promise<Settings> => {
        const res = await fetch(`${API_URL}/settings`);
        if (!res.ok) throw new Error('Failed to fetch settings');
        return res.json();
    },

    updateSettings: async (settings: Settings): Promise<Settings> => {
        const res = await fetch(`${API_URL}/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings),
        });
        if (!res.ok) throw new Error('Failed to update settings');
        return res.json();
    },

    getDashboardStats: async (): Promise<DashboardSummary> => {
        const res = await fetch(`${API_URL}/dashboard/summary`);
        if (!res.ok) throw new Error('Failed to fetch dashboard stats');
        return res.json();
    },

    submitQuiz: async (sessionId: string, answers: Record<string, string>): Promise<{ quizzes: any[], flashcards: any[] }> => {
        const res = await fetch(`${API_URL}/sessions/${sessionId}/submit_quiz`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(answers),
        });
        if (!res.ok) throw new Error('Failed to submit quiz');
        return res.json();
    },

    resetData: async (): Promise<void> => {
        const res = await fetch(`${API_URL}/admin/reset`, {
            method: 'DELETE',
        });
        if (!res.ok) throw new Error('Failed to reset data');
    },

    getPlacementQuestions: async (): Promise<{ id: number, text: string, options: string[] }[]> => {
        const res = await fetch(`${API_URL}/placement/questions`);
        if (!res.ok) throw new Error('Failed to fetch questions');
        return res.json();
    },

    submitPlacementTest: async (answers: Record<number, string>): Promise<any> => {
        const res = await fetch(`${API_URL}/placement/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answers }),
        });
        if (!res.ok) throw new Error('Failed to submit test');
        return res.json();
    },

    getRecentTopics: async (): Promise<{ code: string, label: string, description: string }[]> => {
        const res = await fetch(`${API_URL}/sessions/recent-topics`);
        return res.ok ? res.json() : [];
    },

    getSessionsHistory: async (): Promise<SessionResponse[]> => {
        const res = await fetch(`${API_URL}/sessions/history`);
        if (!res.ok) throw new Error('Failed to fetch history');
        return res.json();
    }
};
