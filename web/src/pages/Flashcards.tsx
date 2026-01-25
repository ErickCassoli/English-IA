import { useEffect, useState } from "react";
import { Plus, RotateCcw } from "lucide-react";
import { api } from "../services/api";
import { Button } from "../components/ui/button";

interface Flashcard {
  id: string;
  front: string;
  back: string;
  reps: number;
}

export default function Flashcards() {
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCards();
  }, []);

  const loadCards = async () => {
    try {
      setLoading(true);
      const data = await api.getDueFlashcards();
      setCards(data);
      setCurrentIndex(0);
      setIsFlipped(false);
    } catch (error) {
      console.error("Failed to load cards:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (quality: number) => {
    const card = cards[currentIndex];
    if (!card) return;

    try {
      await api.reviewFlashcard(card.id, quality);
      
      // Move to next card
      if (currentIndex < cards.length - 1) {
        setCurrentIndex(prev => prev + 1);
        setIsFlipped(false);
      } else {
        // Finished all cards
        setCards([]); // Clear to show empty state
      }
    } catch (error) {
      console.error("Failed to submit review:", error);
    }
  };

  if (loading) {
     return <div className="text-slate-400 text-center p-12">Loading flashcards...</div>;
  }

  const currentCard = cards[currentIndex];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
         <div>
            <h1 className="text-3xl font-bold text-white tracking-tight text-amber-100">Flashcards</h1>
            <p className="text-slate-400 mt-2">{cards.length > 0 ? `${cards.length - currentIndex} cards remaining` : "No pending cards"}</p>
         </div>
         <Button className="bg-cyan-500 hover:bg-cyan-600">
            <Plus className="h-4 w-4 mr-2" /> Add Card
         </Button>
      </div>

      <div className="flex items-center justify-center min-h-[500px]">
        {cards.length === 0 || !currentCard ? (
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-12 text-center max-w-md w-full">
                <RotateCcw className="h-16 w-16 text-slate-600 mx-auto mb-6" />
                <h3 className="text-xl font-semibold text-slate-200">No cards to review!</h3>
                <p className="text-slate-500 mt-2 mb-8">All caught up for today. Add new cards to continue learning.</p>
                <div className="flex gap-4 justify-center">
                    <Button variant="outline" onClick={loadCards}>
                        <RotateCcw className="h-4 w-4 mr-2" /> Refresh
                    </Button>
                    <Button className="bg-cyan-500 hover:bg-cyan-600">
                        <Plus className="h-4 w-4 mr-2" /> Add Card
                    </Button>
                </div>
            </div>
        ) : (
             <div className="w-full max-w-2xl perspective-1000">
                {/* Card Container */}
                <div 
                    className="relative w-full aspect-[16/9] cursor-pointer group"
                    onClick={() => !isFlipped && setIsFlipped(true)}
                >
                    <div className={`
                        w-full h-full transition-all duration-500 preserve-3d
                        ${isFlipped ? "rotate-y-180" : ""}
                    `}>
                        {/* Front */}
                        <div className="absolute inset-0 backface-hidden bg-slate-800 border-2 border-slate-700 rounded-2xl flex flex-col items-center justify-center p-8 shadow-2xl hover:border-cyan-500/50 transition-colors">
                            <span className="text-sm font-medium text-cyan-400 mb-4 uppercase tracking-wider">Front</span>
                            <h2 className="text-3xl md:text-4xl font-bold text-white text-center">
                                {currentCard.front}
                            </h2>
                            <p className="text-slate-500 mt-8 text-sm absolute bottom-8">Click to show answer</p>
                        </div>

                        {/* Back */}
                        <div className="absolute inset-0 backface-hidden rotate-y-180 bg-slate-900 border-2 border-slate-700 rounded-2xl flex flex-col items-center justify-center p-8 shadow-2xl">
                             <span className="text-sm font-medium text-emerald-400 mb-4 uppercase tracking-wider">Back</span>
                             <h2 className="text-2xl md:text-3xl font-medium text-slate-200 text-center">
                                {currentCard.back}
                            </h2>
                        </div>
                    </div>
                </div>

                {/* Controls */}
                <div className={`mt-8 transition-opacity duration-300 ${isFlipped ? "opacity-100" : "opacity-0 pointer-events-none"}`}>
                    <div className="flex justify-center gap-4">
                        <Button 
                            variant="destructive" 
                            className="w-24 bg-red-500/10 hover:bg-red-500/20 text-red-500 border-red-500/50"
                            onClick={() => handleReview(1)}
                        >
                            Again
                        </Button>
                        <Button 
                            variant="outline" 
                            className="w-24 border-slate-600 hover:bg-slate-800"
                            onClick={() => handleReview(3)}
                        >
                            Hard
                        </Button>
                        <Button 
                            variant="outline"
                            className="w-24 border-cyan-500/50 text-cyan-400 hover:bg-cyan-950"
                             onClick={() => handleReview(4)}
                        >
                            Good
                        </Button>
                        <Button 
                            className="w-24 bg-emerald-500 hover:bg-emerald-600 text-white"
                             onClick={() => handleReview(5)}
                        >
                            Easy
                        </Button>
                    </div>
                </div>
             </div>
        )}
      </div>
    </div>
  );
}
