import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { MessageSquare, Globe, Laptop, Coffee, Briefcase, Music, Sun, Plus, Gamepad2, Heart, ShoppingBag, Leaf, Landmark, UserCheck, Share2, Users, GraduationCap, AlertTriangle } from "lucide-react";
import { api, type PracticeTopic } from "../services/api";
import { Button } from "../components/ui/button";

// Helper to get icon based on topic code (simple mapping)
const getIcon = (code: string) => {
    switch(code) {
        case 'travel': return <Globe className="h-6 w-6 text-emerald-400" />;
        case 'technology': return <Laptop className="h-6 w-6 text-blue-400" />;
        case 'food': return <Coffee className="h-6 w-6 text-amber-400" />;
        case 'work': return <Briefcase className="h-6 w-6 text-slate-400" />;
        case 'entertainment': return <Music className="h-6 w-6 text-purple-400" />;
        case 'gaming': return <Gamepad2 className="h-6 w-6 text-indigo-400" />;
        case 'daily_life': return <Sun className="h-6 w-6 text-yellow-400" />;
        case 'health': return <Heart className="h-6 w-6 text-rose-400" />;
        case 'shopping': return <ShoppingBag className="h-6 w-6 text-pink-400" />;
        case 'nature': return <Leaf className="h-6 w-6 text-green-400" />;
        case 'history': return <Landmark className="h-6 w-6 text-stone-400" />;
        case 'job_interview': return <UserCheck className="h-6 w-6 text-blue-400" />;
        case 'social_media': return <Share2 className="h-6 w-6 text-sky-400" />;
        case 'relationships': return <Users className="h-6 w-6 text-rose-300" />;
        case 'education': return <GraduationCap className="h-6 w-6 text-indigo-300" />;
        default: return <MessageSquare className="h-6 w-6 text-cyan-400" />;
    }
};

const getGradient = (code: string) => {
    switch(code) {
        case 'travel': return "from-emerald-900/40 to-emerald-500/10 hover:border-emerald-500/50";
        case 'technology': return "from-blue-900/40 to-blue-500/10 hover:border-blue-500/50";
        case 'food': return "from-amber-900/40 to-amber-500/10 hover:border-amber-500/50";
        case 'entertainment': return "from-purple-900/40 to-purple-500/10 hover:border-purple-500/50";
        case 'gaming': return "from-indigo-900/40 to-indigo-500/10 hover:border-indigo-500/50";
        case 'health': return "from-rose-900/40 to-rose-500/10 hover:border-rose-500/50";
        case 'shopping': return "from-pink-900/40 to-pink-500/10 hover:border-pink-500/50";
        case 'nature': return "from-green-900/40 to-green-500/10 hover:border-green-500/50";
        case 'history': return "from-stone-800 to-stone-600/10 hover:border-stone-500/50";
        case 'social_media': return "from-sky-900/40 to-sky-500/10 hover:border-sky-500/50";
        default: return "from-slate-800 to-slate-800/50 hover:border-cyan-500/50";
    }
};

function SkeletonTopicCard() {
  return (
    <div className="glass-card rounded-2xl p-6 space-y-4 border border-slate-700">
      <div className="skeleton h-12 w-12 rounded-xl" />
      <div className="skeleton h-5 w-32" />
      <div className="space-y-2">
        <div className="skeleton h-3 w-full" />
        <div className="skeleton h-3 w-3/4" />
      </div>
    </div>
  );
}

export default function Practice() {
  const navigate = useNavigate();
  const [topics, setTopics] = useState<PracticeTopic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getTopics()
      .then(setTopics)
      .catch(() => setError("Could not load topics. Is the backend running?"))
      .finally(() => setLoading(false));
  }, []);

  const handleStart = (topicCode: string) => {
    navigate(`/chat?topic=${topicCode}`);
  };

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4 text-center">
        <div className="h-16 w-16 bg-red-500/10 rounded-full flex items-center justify-center ring-1 ring-red-500/20">
          <AlertTriangle className="h-8 w-8 text-red-400" />
        </div>
        <p className="text-slate-400 max-w-sm">{error}</p>
        <Button onClick={() => window.location.reload()} className="bg-cyan-500 hover:bg-cyan-600">
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight gradient-text">Themed Practice</h1>
        <p className="text-slate-400 mt-2">Choose a topic to start a focused conversation session with your AI tutor.</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 stagger">
          {Array.from({ length: 6 }).map((_, i) => <SkeletonTopicCard key={i} />)}
        </div>
      ) : null}

      <div className={loading ? "hidden" : "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 stagger"}>
        {topics.map(topic => (
            <button
                key={topic.code}
                onClick={() => handleStart(topic.code)}
                className={`
                    relative group p-6 rounded-2xl border border-slate-700/80
                    bg-gradient-to-br ${getGradient(topic.code)}
                    transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl text-left focus:outline-none focus:ring-2 focus:ring-cyan-500/50
                `}
            >
                <div className="mb-4 bg-slate-900/50 w-12 h-12 rounded-xl flex items-center justify-center border border-slate-700 group-hover:border-white/20 transition-colors">
                    {getIcon(topic.code)}
                </div>
                <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-cyan-400 transition-colors">
                    {topic.label}
                </h3>
                <p className="text-slate-400 text-sm leading-relaxed">
                    {topic.description}
                </p>
            </button>
        ))}

        {/* Custom Topic Card */}
        <button
            onClick={() => navigate('/chat')} // Chat handles custom topic selector if no param
            className="
                relative group p-6 rounded-2xl border-2 border-dashed border-slate-700 
                hover:border-slate-500 hover:bg-slate-800/30
                transition-all duration-300 text-left flex flex-col items-center justify-center text-center space-y-3
            "
        >
            <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center group-hover:bg-cyan-500/20 transition-colors">
                <Plus className="w-6 h-6 text-slate-400 group-hover:text-cyan-400" />
            </div>
            <div>
                <h3 className="text-lg font-medium text-white">Custom Topic</h3>
                <p className="text-slate-500 text-sm">Create your own scenario</p>
            </div>
        </button>
      </div>
    </div>
  );
}
