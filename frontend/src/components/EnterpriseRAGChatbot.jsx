import React, { useState } from 'react';
import axios from 'axios';

const EnterpriseRAGChatbot = () => {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!question.trim()) return;

    setLoading(true);
    try {
      const res = await axios.post('https://ai-project-2o04.onrender.com/chat', {
        question: question.trim(),
      });
      setResponse(res.data.answer);
    } catch (error) {
      console.error(error);
      setResponse('Đã xảy ra lỗi. Không thể lấy câu trả lời từ backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2>🤖 Enterprise RAG Chatbot</h2>
      <textarea
        rows={3}
        placeholder="Nhập câu hỏi của bạn..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        style={styles.textarea}
      />
      <button onClick={handleSend} disabled={loading} style={styles.button}>
        {loading ? 'Đang xử lý...' : 'Gửi'}
      </button>
      {response && (
        <div style={styles.response}>
          <strong>Phản hồi:</strong>
          <p>{response}</p>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '600px',
    margin: '40px auto',
    padding: '20px',
    border: '1px solid #ddd',
    borderRadius: '12px',
    background: '#f9f9f9',
    fontFamily: 'Arial, sans-serif',
  },
  textarea: {
    width: '100%',
    padding: '10px',
    fontSize: '16px',
    marginBottom: '12px',
  },
  button: {
    padding: '10px 20px',
    fontSize: '16px',
    cursor: 'pointer',
  },
  response: {
    marginTop: '20px',
    background: '#fff',
    padding: '15px',
    borderRadius: '8px',
    border: '1px solid #ccc',
  },
};

export default EnterpriseRAGChatbot;
