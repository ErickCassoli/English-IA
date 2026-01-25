import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { CheckCircle, ArrowRight, Brain } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { api } from "../services/api";

interface Question {
    id: number;
    text: string;
    options: string[];
}

export default function PlacementTest() {
    const navigate = useNavigate();
    const [questions, setQuestions] = useState<Question[]>([]);
    const [currentIdx, setCurrentIdx] = useState(0);
    const [answers, setAnswers] = useState<Record<number, string>>({});
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        api.getPlacementQuestions().then(setQuestions).catch(console.error);
    }, []);

    const handleSelect = (option: string) => {
        const q = questions[currentIdx];
        setAnswers({ ...answers, [q.id]: option });
    };

    const handleNext = async () => {
        if (currentIdx < questions.length - 1) {
            setCurrentIdx(prev => prev + 1);
        } else {
            // Submit
            setSubmitting(true);
            try {
                await api.submitPlacementTest(answers);
                // Force reload to update Sidebar state
                navigate('/dashboard');
                // window.location.reload(); // If reload is strictly needed for sidebar update, we should check logic. But navigate is better.
            } catch (e) {
                console.error(e);
                alert("Failed to submit test.");
                setSubmitting(false);
            }
        }
    };

    if (questions.length === 0) return <div className="p-10 text-white">Loading test...</div>;

    const currentQ = questions[currentIdx];
    const progress = ((currentIdx + 1) / questions.length) * 100;

    return (
        <div className="max-w-2xl mx-auto py-12 px-4 animate-in fade-in slide-in-from-bottom-4">
            <div className="mb-8 text-center">
                <div className="mx-auto w-16 h-16 bg-amber-500/20 rounded-full flex items-center justify-center mb-4 ring-1 ring-amber-500/50">
                    <Brain className="h-8 w-8 text-amber-500" />
                </div>
                <h1 className="text-3xl font-bold text-white">Placement Test</h1>
                <p className="text-slate-400 mt-2">Question {currentIdx + 1} of {questions.length}</p>
            </div>

            {/* Progress Bar */}
            <div className="w-full h-2 bg-slate-800 rounded-full mb-8 overflow-hidden">
                <div 
                    className="h-full bg-gradient-to-r from-amber-500 to-orange-500 transition-all duration-300"
                    style={{ width: `${progress}%` }}
                />
            </div>

            <Card className="glass-card border-slate-700">
                <CardContent className="p-8 space-y-8">
                    <h2 className="text-xl font-medium text-white">{currentQ.text}</h2>
                    
                    <div className="space-y-3">
                        {currentQ.options.map(opt => {
                            const isSelected = answers[currentQ.id] === opt;
                            return (
                                <div 
                                    key={opt}
                                    onClick={() => handleSelect(opt)}
                                    className={`
                                        p-4 rounded-xl border cursor-pointer transition-all flex items-center justify-between group
                                        ${isSelected 
                                            ? 'bg-amber-500/20 border-amber-500 text-white shadow-[0_0_15px_rgba(245,158,11,0.2)]' 
                                            : 'bg-slate-800/50 border-slate-700 text-slate-300 hover:bg-slate-800 hover:border-slate-600'}
                                    `}
                                >
                                    <span className="font-medium">{opt}</span>
                                    {isSelected && <CheckCircle className="h-5 w-5 text-amber-500" />}
                                </div>
                            );
                        })}
                    </div>

                    <div className="flex justify-end pt-4">
                        <Button 
                            onClick={handleNext}
                            disabled={!answers[currentQ.id] || submitting}
                            className="bg-white text-slate-900 hover:bg-slate-200 font-bold px-8 h-12"
                        >
                            {currentIdx === questions.length - 1 ? (
                                submitting ? "Analyzing..." : "Submit Test"
                            ) : (
                                <>Next Question <ArrowRight className="ml-2 h-4 w-4" /></>
                            )}
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
