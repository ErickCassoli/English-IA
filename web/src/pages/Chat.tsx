import { useEffect, useRef, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Send, Bot, User, Sparkles, Flag } from "lucide-react";
import { api, type ChatMessage } from "../services/api";
import { Button } from "../components/ui/button";
import { cn } from "../lib/utils";
import { CorrectionPopover } from "../components/correction-popover";
import { TopicSelector } from "../components/TopicSelector";

export default function Chat() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(searchParams.get("session_id"));
  const [loading, setLoading] = useState(false);
  const [finishing, setFinishing] = useState(false);
  const [showSelector, setShowSelector] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);



  useEffect(() => {
    const topic = searchParams.get("topic");
    const existingSession = searchParams.get("session_id");

    if (existingSession) {
        setSessionId(existingSession);
        api.getHistory(existingSession).then(setMessages).catch(console.error);
    } else if (topic) {
        api.createSession(topic).then(res => {
            setSessionId(res.session_id);
            setSearchParams({ session_id: res.session_id });
        }).catch(err => {
            console.error(err);
            navigate('/dashboard'); 
        });
    } else {
        // No session, no topic -> Show selection
        setShowSelector(true);
    }
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleTopicSelect = async (code: string | null, custom?: string) => {
      setLoading(true);
      try {
          const res = await api.createSession(code, custom);
          setSessionId(res.session_id);
          setSearchParams({ session_id: res.session_id });
          setShowSelector(false);
          // Optional: Send initial greeting or prompt
      } catch (e) {
          console.error(e);
          alert("Failed to start session");
      } finally {
          setLoading(false);
      }
  };

  const handleSend = async () => {
    if (!input.trim() || loading || showSelector) return;
    const text = input;
    setInput("");
    setLoading(true);

    if (sessionId) {
        await sendMessage(sessionId, text);
    }
  };

  const sendMessage = async (sid: string, text: string) => {
    const tempMsg: ChatMessage = { role: "user", text };
    setMessages(prev => [...prev, tempMsg]);
    
    try {
        const res = await api.sendMessage(sid, text);
        setMessages(prev => [...prev, { 
            role: "assistant", 
            text: res.reply,
            detected_errors: res.detected_errors 
        }]);
    } catch (err) {
        console.error(err);
    } finally {
        setLoading(false);
    }
  };

  const handleFinish = async () => {
      if (!sessionId) return;
      setFinishing(true);
      try {
          await api.finishSession(sessionId);
          navigate(`/quiz/${sessionId}`); 
      } catch (e) {
          console.error("Failed to finish session", e);
          setFinishing(false);
      }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] relative">
      {/* Topic Selector Overlay */}
      {showSelector && (
          <TopicSelector onSelect={handleTopicSelect} />
      )}

      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight flex items-center">
                Practice English
                {sessionId && <div className="ml-3 h-2 w-2 rounded-full bg-green-500 animate-pulse" />}
            </h1>
            <p className="text-slate-400 mt-1 flex items-center">
                <Sparkles className="w-4 h-4 mr-1 text-cyan-400" />
                AI Tutor customized for you
            </p>
          </div>
          {messages.length > 0 && (
             <Button 
                variant="outline" 
                className="border-red-500/20 text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-colors"
                onClick={handleFinish}
                disabled={finishing || loading}
             >
                {finishing ? (
                    "Generating Review..."
                ) : (
                    <>
                        <Flag className="mr-2 h-4 w-4" /> Finish Session
                    </>
                )}
             </Button>
          )}
      </div>

      {/* Chat Area */}
      <div className="flex-1 glass-card rounded-2xl p-6 overflow-y-auto mb-4 relative min-h-[400px] flex flex-col space-y-6 scroll-smooth">
        {messages.length === 0 && !showSelector && (
             <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-8 z-0">
                <div className="h-20 w-20 bg-cyan-500/10 rounded-full flex items-center justify-center mb-6 ring-1 ring-cyan-500/20">
                    <Sparkles className="h-10 w-10 text-cyan-400" />
                </div>
                <p className="text-2xl font-semibold text-white">Start a conversation!</p>
                <p className="text-slate-400 mt-2 max-w-md">Practice your English skills with our AI tutor.</p>
             </div>
        )}
        
        {messages.filter(m => m.role !== 'system').map((msg, i) => (
            <div key={i} className={cn("flex w-full group", msg.role === 'user' ? 'justify-end' : 'justify-start')}>
                <div className={cn(
                    "max-w-[80%] lg:max-w-[70%] flex gap-3",
                    msg.role === 'user' ? "flex-row-reverse" : "flex-row"
                )}>
                    <div className={cn(
                        "flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center",
                        msg.role === 'user' ? "bg-cyan-500" : "bg-violet-600"
                    )}>
                        {msg.role === 'user' ? <User className="h-5 w-5 text-white" /> : <Bot className="h-5 w-5 text-white" />}
                    </div>

                    <div className={cn(
                        "p-4 rounded-2xl text-sm leading-relaxed shadow-md relative",
                        msg.role === 'user' 
                        ? "bg-gradient-to-br from-cyan-500 to-blue-600 text-white rounded-tr-sm" 
                        : "bg-slate-800/80 border border-slate-700/50 text-slate-100 rounded-tl-sm backdrop-blur-sm"
                    )}>
                        <span>{msg.text}</span>
                        {msg.role === 'assistant' && msg.detected_errors && msg.detected_errors.length > 0 && (
                            <CorrectionPopover errors={msg.detected_errors} />
                        )}
                    </div>
                </div>
            </div>
        ))}
        {loading && (
            <div className="flex justify-start w-full">
                    <div className="flex gap-3 max-w-[80%]">
                    <div className="flex-shrink-0 h-8 w-8 rounded-full bg-violet-600 flex items-center justify-center">
                        <Bot className="h-5 w-5 text-white" />
                    </div>
                    <div className="bg-slate-800/80 border border-slate-700/50 p-4 rounded-2xl rounded-tl-sm flex items-center space-x-2">
                        <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-75" />
                        <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-150" />
                    </div>
                    </div>
            </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input Area */}
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-t from-[#0B1120] to-transparent -top-4 pointer-events-none" />
        <div className={cn(
            "relative z-10 bg-slate-800/50 backdrop-blur-xl border border-slate-700 rounded-xl p-2 flex items-center shadow-2xl transition-all",
            showSelector && "opacity-50 pointer-events-none grayscale"
        )}>
            <input 
                className="flex-1 bg-transparent text-white placeholder:text-slate-500 px-4 py-3 focus:outline-none"
                placeholder={showSelector ? "Choose a topic above..." : "Type your message in English..."}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                disabled={loading || finishing || showSelector}
            />



            <Button 
                size="icon"
                className={cn(
                    "h-10 w-10 rounded-lg transition-all",
                    input.trim() ? "bg-cyan-500 hover:bg-cyan-400 text-white shadow-[0_0_10px_rgba(6,182,212,0.5)]" : "bg-slate-700 text-slate-400"
                )}
                onClick={handleSend}
                disabled={!input.trim() || loading || finishing || showSelector}
            >
                <Send className="h-5 w-5" />
            </Button>
        </div>
        <p className="text-xs text-center text-slate-500 mt-2">AI can make mistakes. Practice regularly!</p>
      </div>
    </div>
  );
}
