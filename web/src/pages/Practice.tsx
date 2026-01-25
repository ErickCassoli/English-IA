import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Play } from "lucide-react";
import { api, type PracticeTopic } from "../services/api";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";

const COLORS = [
    { bg: "bg-indigo-500/10", text: "text-indigo-400", dot: "bg-indigo-500" },
    { bg: "bg-purple-500/10", text: "text-purple-400", dot: "bg-purple-500" },
    { bg: "bg-emerald-500/10", text: "text-emerald-400", dot: "bg-emerald-500" },
    { bg: "bg-rose-500/10", text: "text-rose-400", dot: "bg-rose-500" },
    { bg: "bg-amber-500/10", text: "text-amber-400", dot: "bg-amber-500" },
    { bg: "bg-cyan-500/10", text: "text-cyan-400", dot: "bg-cyan-500" },
];

export default function Practice() {
  const [topics, setTopics] = useState<PracticeTopic[]>([]);
  const [isAssessed, setIsAssessed] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Parallel fetch
    Promise.all([
        api.getTopics(),
        api.getDashboardStats()
    ]).then(([topicsData, statsData]) => {
        setTopics(topicsData);
        setIsAssessed(statsData.is_assessed);
    }).catch(console.error);
  }, []);

  const handleStart = async (topicCode: string) => {
    // Special handling for placement: Reset if taking it
    if (topicCode === 'placement_test') {
       if (confirm("This will reset your data to begin the test. Continue?")) {
           try {
               await api.resetData();
               const sess = await api.createSession("placement_test");
               navigate(`/chat?session=${sess.session_id}`);
           } catch {
               alert("Failed.");
           }
       }
       return;
    }
    navigate(`/chat?topic=${topicCode}`);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Themed Practice</h1>
        <p className="text-slate-400 mt-2">Choose a topic and practice conversing in English. Get detailed feedback after each session!</p>
      </div>
      
      {!isAssessed && (
          <div className="bg-amber-500/10 border border-amber-500/20 text-amber-200 p-4 rounded-xl flex items-center">
              <span className="mr-2">⚠️</span> 
              <span>You must complete the <strong>Placement Test</strong> before accessing other topics.</span>
          </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {topics.map((topic, idx) => {
            const theme = COLORS[idx % COLORS.length];
            const isPlacement = topic.code === 'placement_test';
            const isLocked = !isAssessed && !isPlacement;

            return (
                <Card key={topic.code} className={`bg-slate-900/50 border-slate-800 transition-colors ${!isLocked && 'hover:border-slate-700'} ${isLocked && 'opacity-50 grayscale'}`}>
                    <CardContent className="p-6 space-y-4">
                        <div className="flex items-center space-x-2">
                             <div className={`h-3 w-3 rounded-full ${theme.dot}`} />
                             <h3 className="text-xl font-semibold text-slate-200">{topic.label}</h3>
                             {isLocked && <span className="text-xs bg-slate-800 px-2 py-1 rounded text-slate-400">Locked</span>}
                        </div>
                        <p className="text-sm text-slate-400 min-h-[40px]">{topic.description}</p>
                        <Button 
                            className={`w-full font-medium group ${
                                isPlacement 
                                ? 'bg-gradient-to-r from-amber-500 to-orange-600 hover:scale-105 text-white shadow-lg' 
                                : 'bg-cyan-500 hover:bg-cyan-600 text-white'
                            }`}
                            onClick={() => handleStart(topic.code)}
                            disabled={isLocked}
                        >
                            <Play className="h-4 w-4 mr-2 group-hover:fill-current" />
                            {isPlacement ? 'Take Placement Test' : 'Start Practice'}
                        </Button>
                    </CardContent>
                </Card>
            );
        })}
      </div>
    </div>
  );
}
