import { useState } from 'react';
import { Send } from 'lucide-react';

const ChatComposer = ({ onSend, placeholder = 'Ask me anything...', disabled = false }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-3 p-4 bg-white border-t border-border">
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        className="flex-1 px-4 py-2.5 bg-background border border-border rounded-lg text-sm text-primary placeholder:text-secondary focus:outline-none focus:border-accent"
      />
      <button
        type="submit"
        disabled={!message.trim() || disabled}
        className="w-10 h-10 flex items-center justify-center rounded-full bg-accent text-white hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer transition-colors duration-150"
      >
        <Send size={18} />
      </button>
    </form>
  );
};

export default ChatComposer;
