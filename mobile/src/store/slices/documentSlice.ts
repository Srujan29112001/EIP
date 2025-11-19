/**
 * Document Slice
 * Manages document upload and analysis state
 */
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import api from '../../services/api';

interface Document {
  id: string;
  filename: string;
  file_type: string;
  upload_date: string;
  analysis_status: 'pending' | 'processing' | 'completed' | 'failed';
  analysis_result?: {
    summary: string;
    entities: string[];
    insights: string[];
  };
}

interface DocumentState {
  documents: Document[];
  currentAnalysis: {
    text: string;
    entities: Array<{ text: string; type: string }>;
    summary: string;
    insights: string[];
  } | null;
  uploading: boolean;
  analyzing: boolean;
  error: string | null;
}

const initialState: DocumentState = {
  documents: [],
  currentAnalysis: null,
  uploading: false,
  analyzing: false,
  error: null,
};

// Async thunks
export const uploadDocument = createAsyncThunk(
  'document/upload',
  async ({ file, userId }: { file: any; userId: string }, { rejectWithValue }) => {
    try {
      const response = await api.uploadDocument(file, userId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

export const analyzeDocument = createAsyncThunk(
  'document/analyze',
  async (documentId: string, { rejectWithValue }) => {
    try {
      const response = await api.analyzeDocument(documentId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchDocuments = createAsyncThunk(
  'document/fetchAll',
  async (userId: string, { rejectWithValue }) => {
    try {
      const documents = await api.getDocuments(userId);
      return documents;
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

const documentSlice = createSlice({
  name: 'document',
  initialState,
  reducers: {
    clearAnalysis: (state) => {
      state.currentAnalysis = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Upload document
    builder
      .addCase(uploadDocument.pending, (state) => {
        state.uploading = true;
        state.error = null;
      })
      .addCase(uploadDocument.fulfilled, (state, action) => {
        state.uploading = false;
        state.documents.push(action.payload);
      })
      .addCase(uploadDocument.rejected, (state, action) => {
        state.uploading = false;
        state.error = action.payload as string;
      });

    // Analyze document
    builder
      .addCase(analyzeDocument.pending, (state) => {
        state.analyzing = true;
        state.error = null;
      })
      .addCase(analyzeDocument.fulfilled, (state, action) => {
        state.analyzing = false;
        state.currentAnalysis = action.payload;
      })
      .addCase(analyzeDocument.rejected, (state, action) => {
        state.analyzing = false;
        state.error = action.payload as string;
      });

    // Fetch documents
    builder
      .addCase(fetchDocuments.fulfilled, (state, action) => {
        state.documents = action.payload;
      });
  },
});

export const { clearAnalysis, clearError } = documentSlice.actions;
export default documentSlice.reducer;
