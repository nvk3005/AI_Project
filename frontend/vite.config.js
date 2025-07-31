import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/enterprise-rag-chatbot/', // ví dụ: '/enterprise-rag-chatbot/'
});
