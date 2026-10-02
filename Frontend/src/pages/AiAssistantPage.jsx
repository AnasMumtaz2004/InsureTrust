import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, MessageSquare, Shield } from 'lucide-react';
import { ChatComposer, IconButton } from '../components/shared';
import AiAvatar from '../assets/AiAvatar';
import { useAuth } from '../auth/useAuth';
import { postClaimChat, getClaims } from '../api/clientApi';

const iconRailItems = [
  { icon: Home, label: 'Home', path: '/dashboard' },
  { icon: MessageSquare, label: 'Chat', path: '/assistant', active: true },
];

const AiAssistantPage = () => {
  const [claims, setClaims] = useState([]);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [claimId, setClaimId] = useState(null);
  const chatEndRef = useRef(null);
  const navigate = useNavigate();
  const { user, token } = useAuth();

  useEffect(() => {
    const loadDefaultClaim = async () => {
      if (!token) return;
      try {
        const claimList = await getClaims(token, 50);
        setClaims(claimList || []);
        if (claimList?.length) {
          setClaimId(claimList[0].id);
          setMessages([{ role: 'assistant', content: `I can help with claim ${claimList[0].claim_number}. Ask me anything about your claim or coverage.` }]);
        } else {
          setClaimId(null);
          setMessages([{ role: 'assistant', content: 'No claims are available yet. File a claim first and then I can help explain it.' }]);
        }
      } catch (error) {
        console.error(error);
      }
    };

    loadDefaultClaim();
  }, [token]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (message) => {
    if (!claimId || !token) {
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Please sign in to chat with the assistant.' }]);
      return;
    }

    setMessages((prev) => [...prev, { role: 'user', content: message }]);
    setLoading(true);

    try {
      const data = await postClaimChat(claimId, message, token);
      setMessages((prev) => [...prev, { role: 'assistant', content: data.reply }]);
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'assistant', content: error.message || 'I could not reach the assistant right now.' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleClaimChange = (event) => {
    const selectedId = event.target.value;
    const selectedClaim = claims.find((claim) => claim.id === selectedId);
    setClaimId(selectedId || null);
    setMessages(selectedClaim
      ? [{ role: 'assistant', content: `I can help with claim ${selectedClaim.claim_number}. Ask me anything about your claim or coverage.` }]
      : []);
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Left icon rail — desktop only */}
      <div className="hidden md:flex flex-col items-center w-16 bg-white border-r border-border py-4 gap-2">
        <div className="mb-4">
          <Shield size={24} className="text-accent" />
        </div>
        {iconRailItems.map((item) => (
          <IconButton
            key={item.label}
            icon={item.icon}
            active={item.active}
            onClick={() => navigate(item.path)}
            title={item.label}
          />
        ))}
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-3 px-4 md:px-6 py-4 bg-white border-b border-border">
          <div className="flex items-center gap-3">
            <AiAvatar size={32} />
            <div>
              <h2 className="text-base font-semibold text-primary">InsureTrust AI Assistant</h2>
              <p className="text-xs text-secondary hidden md:block">Powered by advanced AI agents</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {claims.length > 0 && (
              <label className="flex items-center gap-2">
                <span className="sr-only">Select claim</span>
                <select
                  aria-label="Select claim"
                  value={claimId || ''}
                  onChange={handleClaimChange}
                  className="max-w-48 rounded-md border border-border bg-white px-2 py-2 text-xs text-primary focus:outline-none focus:border-accent sm:max-w-64"
                >
                  {claims.map((claim) => (
                    <option key={claim.id} value={claim.id}>{claim.claim_number} · {claim.status}</option>
                  ))}
                </select>
              </label>
            )}
            <div className="w-8 h-8 rounded-full bg-primary text-white text-xs font-medium flex items-center justify-center">
              {user?.name?.[0] || 'U'}
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-4 md:px-6 py-6 space-y-4">
          {messages.length === 0 ? (
            <div className="text-sm text-secondary">Start a conversation with the assistant.</div>
          ) : (
            messages.map((msg, i) => (
              <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'assistant' && <AiAvatar size={28} className="shrink-0 mt-1" />}
                <div className={`max-w-[80%] md:max-w-[60%]`}>
                  <div className={`px-4 py-3 rounded-lg text-sm leading-relaxed ${msg.role === 'user' ? 'bg-background text-primary border border-border' : 'bg-white text-primary border border-border'}`}>
                    {msg.content}
                  </div>
                </div>
              </div>
            ))
          )}
          {loading && <div className="text-sm text-secondary">Assistant is thinking…</div>}
          <div ref={chatEndRef} />
        </div>

        <div className="pb-16 md:pb-0">
          <ChatComposer onSend={handleSend} />
        </div>
      </div>
    </div>
  );
};

export default AiAssistantPage;
