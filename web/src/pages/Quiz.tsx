import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { CheckCircle, ArrowRight } from "lucide-react";
import { api } from "../services/api";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { RadioGroup, RadioGroupItem } from "../components/ui/radio-group";
import { Label } from "../components/ui/label";

interface QuizItem {
    id: string;
    type: string;
    prompt: string;
    choices_json: string; // JSON string
    answer: string;
}

export default function Quiz() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [quizzes, setQuizzes] = useState<QuizItem[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!sessionId) return;
    api.finishSession(sessionId).then(res => {
         if (res.quizzes && res.quizzes.length > 0) {
             setQuizzes(res.quizzes);
         } else {
             // Handle case with no quizzes?? For now redirect or show empty
             console.warn("No quizzes returned");
         }
         setLoading(false);
    }).catch(console.error);
  }, [sessionId]);

  const handleAnswer = (quizId: string, value: string) => {
      setAnswers(prev => ({ ...prev, [quizId]: value }));
  };

  const handleSubmit = async () => {
    if (!sessionId) return;
    setSubmitting(true);
    try {
        await api.submitQuiz(sessionId, answers);
        navigate(`/report/${sessionId}`); // Will implement report page next
    } catch (e) {
        console.error(e);
        setSubmitting(false);
    }
  };

  if (loading) return <div className="p-8 text-white">Loading quiz...</div>;

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-in fade-in pb-10">
        <div className="text-center">
            <h1 className="text-3xl font-bold text-white mb-2">Knowledge Check</h1>
            <p className="text-slate-400">Review what you practiced in this session</p>
        </div>

        {quizzes.length === 0 ? (
            <Card className="glass-card">
                <CardContent className="p-8 text-center text-slate-400">
                    <CheckCircle className="h-12 w-12 mx-auto mb-4 text-emerald-500" />
                    <p>No quizzes generated for this session. Great job!</p>
                    <Button onClick={() => navigate('/dashboard')} className="mt-4">
                        Back to Dashboard
                    </Button>
                </CardContent>
            </Card>
        ) : (
            <div className="space-y-6">
                {quizzes.map((quiz, index) => {
                    let choices: string[] = [];
                    try {
                        const parsed = JSON.parse(quiz.choices_json);
                        choices = parsed.choices || [];
                    } catch (e) { console.error("Error parsing choices", e); }

                    return (
                        <Card key={quiz.id} className="glass-card border-slate-800">
                            <CardHeader>
                                <CardTitle className="text-lg text-white flex items-start gap-3">
                                    <span className="bg-cyan-500/10 text-cyan-400 text-sm px-2 py-1 rounded-md mt-1">
                                        Q{index + 1}
                                    </span>
                                    <span>{quiz.prompt}</span>
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <RadioGroup onValueChange={(val) => handleAnswer(quiz.id, val)} value={answers[quiz.id]}>
                                    <div className="space-y-3">
                                        {choices.map((choice, i) => (
                                            <div key={i} className="flex items-center space-x-2 rounded-lg border border-slate-700/50 p-3 hover:bg-slate-800/50 transition-colors">
                                                <RadioGroupItem value={choice} id={`q${quiz.id}-c${i}`} className="border-slate-500 text-cyan-500" />
                                                <Label htmlFor={`q${quiz.id}-c${i}`} className="text-slate-300 flex-1 cursor-pointer">
                                                    {choice}
                                                </Label>
                                            </div>
                                        ))}
                                    </div>
                                </RadioGroup>
                            </CardContent>
                        </Card>
                    );
                })}

                <div className="flex justify-end pt-4">
                    <Button 
                        onClick={handleSubmit} 
                        disabled={submitting || Object.keys(answers).length < quizzes.length} 
                        className="bg-cyan-500 hover:bg-cyan-600 text-white px-8 py-6 text-lg shadow-[0_0_20px_rgba(6,182,212,0.3)] transition-all hover:scale-105"
                    >
                        {submitting ? "Analyzing..." : (
                            <>Submit & Analyze <ArrowRight className="ml-2 h-5 w-5" /></>
                        )}
                    </Button>
                </div>
            </div>
        )}
    </div>
  );
}
