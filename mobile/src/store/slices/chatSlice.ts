/**
 * Chat Slice
 * Manages chat/conversation state with AI advisor
 */
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import api from '../../services/api';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  agent_used?: string;
  sources?: Array<{ title: string; url: string }>;
}

interface ChatState {
  messages: Message[];
  sessionId: string | null;
  loading: boolean;
  error: string | null;
  typing: boolean;
}

const initialState: ChatState = {
  messages: [],
  sessionId: null,
  loading: false,
  error: null,
  typing: false,
};

// Async thunks
export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async (
    { query, sessionId }: { query: string; sessionId: string },
    { rejectWithValue }
  ) => {
    try {
      const response = await api.sendChatMessage(query, sessionId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<Message>) => {
      state.messages.push(action.payload);
    },
    clearMessages: (state) => {
      state.messages = [];
      state.sessionId = null;
    },
    setSessionId: (state, action: PayloadAction<string>) => {
      state.sessionId = action.payload;
    },
    setTyping: (state, action: PayloadAction<boolean>) => {
      state.typing = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.loading = true;
        state.typing = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.loading = false;
        state.typing = false;

        // Add assistant message
        const assistantMessage: Message = {
          id: Date.now().toString(),
          role: 'assistant',
          content: action.payload.answer,
          timestamp: new Date(),
          agent_used: action.payload.agent_used,
          sources: action.payload.sources,
        };
        state.messages.push(assistantMessage);
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.loading = false;
        state.typing = false;
        state.error = action.payload as string;
      });
  },
});

export const { addMessage, clearMessages, setSessionId, setTyping } = chatSlice.actions;
export default chatSlice.reducer;
