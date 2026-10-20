import React, { useEffect, useRef, useState, useCallback } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Plus, Send, Trash2, MessageSquare, Loader2, Sparkles } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import { useAuth } from '../context/AuthContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const NAVY = '#1b2a8f';
const RED = '#c8102e';
const SUGGESTIONS = [
  'Quantas OSs Hisense estão aguardando peças?',
  'Liste todas as OSs próximas do bairro Renascença',
  'Como fazer o diagnóstico de um defeito segundo o manual?',
];

// Markdown mínimo estilo ChatGPT: **negrito**, títulos, listas '-'/'1.'; descarta tabelas/separadores se vierem.
const Inline = ({ text }) => text.split(/(\*\*[^*]+\*\*)/g).map((p, i) =>
  p.startsWith('**') && p.endsWith('**') ? <strong key={i}>{p.slice(2, -2)}</strong> : <React.Fragment key={i}>{p}</React.Fragment>);

const cleanLine = (line) => {
  if (/^\s*(\|?\s*:?-{2,}:?\s*)+\|?\s*$/.test(line) || /^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(line) || /^\s*```/.test(line)) return null;
  let l = line.replace(/^\s*>\s?/, '');
  if (/^\s*\|.*\|\s*$/.test(l)) l = l.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim()).filter(Boolean).join(' — ');
  return l;
};

const MessageBody = ({ content }) => (
  <div className="space-y-1.5 text-[15px] leading-relaxed break-words">
    {content.split('\n').map(cleanLine).filter(l => l !== null).map((line, i) => {
      const h = line.match(/^#{1,4}\s+(.*)/);
      if (h) return <p key={i} className="font-semibold pt-2" style={{ color: NAVY }}><Inline text={h[1]} /></p>;
      const b = line.match(/^(\s*)[-*•]\s+(.*)/);
      if (b) return <div key={i} className="flex gap-2" style={{ paddingLeft: b[1].length ? 16 : 4 }}><span className="text-gray-400">•</span><span><Inline text={b[2]} /></span></div>;
      const n = line.match(/^\s*(\d+)[.)]\s+(.*)/);
      if (n) return <div key={i} className="flex gap-2 pl-1"><span className="font-medium text-gray-500 min-w-[1.25rem]">{n[1]}.</span><span><Inline text={n[2]} /></span></div>;
      return line.trim() ? <p key={i} className="whitespace-pre-wrap"><Inline text={line} /></p> : <div key={i} className="h-1" />;
    })}
  </div>
);

const Bubble = ({ m }) => {
  const mine = m.role === 'user';
  return (
    <div className={`flex gap-3 ${mine ? 'justify-end' : ''}`} data-testid={`mi-message-${m.role}`}>
      {!mine && (
        <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold shrink-0" style={{ background: RED }}>Mi</div>
      )}
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${mine ? 'text-white rounded-br-sm' : 'bg-white border border-gray-200 rounded-bl-sm text-gray-800'}`}
        style={mine ? { background: NAVY } : undefined}
      >
        <MessageBody content={m.content} />
      </div>
    </div>
  );
};

const ConversationList = ({ convs, activeId, onSelect, onNew, onDelete }) => (
  <aside className="hidden md:flex w-64 shrink-0 flex-col border-r border-gray-200 bg-white" data-testid="mi-conversation-list">
    <div className="p-3">
      <button onClick={onNew} className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-white text-sm font-medium transition-opacity hover:opacity-90" style={{ background: NAVY }} data-testid="mi-new-conversation-btn">
        <Plus size={16} /> Nova conversa
      </button>
    </div>
    <div className="flex-1 overflow-y-auto px-2 pb-3 space-y-1">
      {convs.map(c => (
        <div key={c.id} className={`group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer text-sm transition-colors ${c.id === activeId ? 'bg-gray-100 font-medium' : 'hover:bg-gray-50'}`}
          onClick={() => onSelect(c.id)} data-testid={`mi-conversation-${c.id}`}>
          <MessageSquare size={14} className="text-gray-400 shrink-0" />
          <span className="truncate flex-1 text-gray-700">{c.title}</span>
          <button onClick={(e) => { e.stopPropagation(); onDelete(c.id); }} className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-600 transition-opacity" data-testid={`mi-delete-${c.id}`}>
            <Trash2 size={14} />
          </button>
        </div>
      ))}
      {convs.length === 0 && <p className="text-xs text-gray-400 px-3 py-2">Nenhuma conversa ainda.</p>}
    </div>
  </aside>
);

const EmptyState = ({ onPick }) => (
  <div className="h-full flex flex-col items-center justify-center text-center px-4" data-testid="mi-empty-state">
    <div className="w-14 h-14 rounded-2xl flex items-center justify-center text-white text-xl font-bold mb-4" style={{ background: RED }}>Mi</div>
    <h2 className="text-2xl font-semibold text-gray-900" style={{ fontFamily: 'Manrope, sans-serif' }}>Como posso ajudar?</h2>
    <p className="text-sm text-gray-500 mt-1">Pergunte sobre qualquer OS ou sobre os manuais técnicos.</p>
    <div className="grid gap-2 mt-6 w-full max-w-md">
      {SUGGESTIONS.map(s => (
        <button key={s} onClick={() => onPick(s)} className="text-left text-sm px-4 py-3 rounded-xl border border-gray-200 bg-white hover:border-gray-400 transition-colors flex items-center gap-2" data-testid="mi-suggestion-btn">
          <Sparkles size={14} style={{ color: RED }} /> {s}
        </button>
      ))}
    </div>
  </div>
);

export default function MiPage() {
  const { token } = useAuth();
  const auth = useCallback(() => ({ headers: { Authorization: `Bearer ${token}` } }), [token]);
  const [convs, setConvs] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const endRef = useRef(null);

  const loadConvs = useCallback(async () => {
    try { setConvs((await axios.get(`${API}/mi/conversations`, auth())).data); } catch { /* ignore */ }
  }, [auth]);

  useEffect(() => { loadConvs(); }, [loadConvs]);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, sending]);

  const selectConv = async (id) => {
    setActiveId(id);
    try { setMessages((await axios.get(`${API}/mi/conversations/${id}/messages`, auth())).data); }
    catch { toast.error('Erro ao carregar conversa'); }
  };

  const newConv = () => { setActiveId(null); setMessages([]); };

  const deleteConv = async (id) => {
    await axios.delete(`${API}/mi/conversations/${id}`, auth()).catch(() => {});
    if (id === activeId) newConv();
    loadConvs();
  };

  const send = async (text) => {
    const msg = (text ?? input).trim();
    if (!msg || sending) return;
    setInput('');
    setMessages(prev => [...prev, { id: `tmp-${Date.now()}`, role: 'user', content: msg }]);
    setSending(true);
    try {
      const res = await axios.post(`${API}/mi/chat`, { message: msg, conversation_id: activeId }, auth());
      setActiveId(res.data.conversation_id);
      setMessages(prev => [...prev, res.data.message]);
      loadConvs();
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Erro ao falar com a Mi');
    } finally {
      setSending(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="flex h-[calc(100vh-8rem)] lg:h-[calc(100vh-10rem)] rounded-xl border border-gray-200 overflow-hidden bg-gray-50" data-testid="mi-page">
        <ConversationList convs={convs} activeId={activeId} onSelect={selectConv} onNew={newConv} onDelete={deleteConv} />
        <section className="flex-1 flex flex-col min-w-0">
          <div className="md:hidden p-2 border-b border-gray-200 bg-white">
            <button onClick={newConv} className="flex items-center gap-1 text-xs font-medium" style={{ color: NAVY }} data-testid="mi-new-conversation-mobile-btn"><Plus size={14} /> Nova conversa</button>
          </div>
          <div className="flex-1 overflow-y-auto px-4 py-6" data-testid="mi-messages">
            {messages.length === 0 ? <EmptyState onPick={send} /> : (
              <div className="max-w-3xl mx-auto space-y-5">
                {messages.map(m => <Bubble key={m.id} m={m} />)}
                {sending && (
                  <div className="flex items-center gap-2 text-sm text-gray-500" data-testid="mi-thinking">
                    <Loader2 size={16} className="animate-spin" style={{ color: RED }} /> Mi está consultando OSs e manuais...
                  </div>
                )}
                <div ref={endRef} />
              </div>
            )}
          </div>
          <form onSubmit={(e) => { e.preventDefault(); send(); }} className="p-3 border-t border-gray-200 bg-white">
            <div className="max-w-3xl mx-auto flex items-end gap-2 rounded-2xl border border-gray-300 px-3 py-2 focus-within:border-gray-500 transition-colors">
              <textarea
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
                rows={1}
                placeholder="Pergunte à Mi sobre OSs ou manuais..."
                className="flex-1 resize-none outline-none text-sm max-h-40 py-1.5 bg-transparent"
                data-testid="mi-input"
              />
              <button type="submit" disabled={sending || !input.trim()} className="w-9 h-9 rounded-full flex items-center justify-center text-white disabled:opacity-40 transition-opacity" style={{ background: RED }} data-testid="mi-send-btn">
                <Send size={16} />
              </button>
            </div>
          </form>
        </section>
      </div>
    </DashboardLayout>
  );
}
