import { useEffect, useState } from "react";
import { Save, Server, Cpu, CheckCircle } from "lucide-react";
import { api, type Settings as SettingsType } from "../services/api";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsType>({ llm_provider: "simple_mock", llm_model: "mock-1" });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    api.getSettings()
        .then(setSettings)
        .catch(console.error)
        .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSuccess(false);
    try {
        const updated = await api.updateSettings(settings);
        setSettings(updated);
        setSuccess(true);
        setTimeout(() => setSuccess(false), 3000);
    } catch (e) {
        console.error(e);
    } finally {
        setSaving(false);
    }
  };

  if (loading) return <div className="p-8 text-slate-400">Loading settings...</div>;

  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Settings</h1>
        <p className="text-slate-400 mt-2">Configure your local AI Tutor environment.</p>
      </div>

      <div className="grid gap-6">
        {/* AI Provider Settings */}
        <Card className="glass-card border-slate-800">
            <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-xl text-white">
                    <Server className="h-5 w-5 text-cyan-400" />
                    <span>AI Provider</span>
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
                <div>
                    <label className="block text-sm font-medium text-slate-400 mb-3">Select Provider</label>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {['ollama', 'openai', 'simple_mock'].map((provider) => (
                            <div 
                                key={provider}
                                onClick={() => setSettings({ ...settings, llm_provider: provider })}
                                className={`cursor-pointer rounded-xl border p-4 transition-all hover:bg-slate-800/50 ${
                                    settings.llm_provider === provider 
                                    ? 'bg-cyan-500/10 border-cyan-500/50 ring-1 ring-cyan-500/20' 
                                    : 'bg-slate-900/40 border-slate-800'
                                }`}
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <span className="font-semibold text-white capitalize">{provider.replace('_', ' ')}</span>
                                    {settings.llm_provider === provider && <CheckCircle className="h-4 w-4 text-cyan-400" />}
                                </div>
                                <p className="text-xs text-slate-500">
                                    {provider === 'ollama' && "Local & Private (Recommended)"}
                                    {provider === 'openai' && "Cloud API (Requires Key)"}
                                    {provider === 'simple_mock' && "For testing UI without AI"}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-slate-400 mb-2">Model Name</label>
                    <div className="relative">
                        <Cpu className="absolute left-3 top-3 h-5 w-5 text-slate-500" />
                        <input 
                            value={settings.llm_model} 
                            onChange={(e) => setSettings({ ...settings, llm_model: e.target.value })}
                            className="w-full bg-slate-900/50 border border-slate-800 rounded-lg py-2.5 pl-10 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50 transition-all placeholder:text-slate-600"
                            placeholder="e.g. llama3, gpt-4o, mock-v1"
                        />
                    </div>
                    <p className="text-xs text-slate-500 mt-2">
                        For Ollama, use models like <code>llama3</code>, <code>mistral</code>, or <code>gemma</code>. Ensure the model is pulled (`ollama pull llama3`).
                    </p>
                </div>
            </CardContent>
        </Card>

        <div className="flex justify-end">
            <Button 
                onClick={handleSave} 
                className="bg-cyan-500 hover:bg-cyan-600 text-white px-8 h-12 text-base shadow-[0_0_20px_rgba(6,182,212,0.3)] transition-all hover:scale-105"
                disabled={saving}
            >
                {saving ? (
                    "Saving..."
                ) : (
                    <>
                        <Save className="mr-2 h-4 w-4" /> Save Configuration
                    </>
                )}
            </Button>
        </div>

        {/* Data Management Section */}
        <Card className="glass-card border-slate-800 bg-red-950/10">
            <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-xl text-red-400">
                    <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse mr-2" />
                    <span>Danger Zone</span>
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="flex items-center justify-between">
                    <div>
                        <h4 className="text-white font-medium">Reset All Data</h4>
                        <p className="text-sm text-slate-400">Irreversibly wipe all sessions, progress, and history.</p>
                    </div>
                    <Button 
                        variant="destructive" 
                        onClick={async () => {
                            if(confirm("Are you ABSOLUTELY sure? This cannot be undone.")) {
                                try {
                                    await api.resetData();
                                    alert("Data reset successfully.");
                                    window.location.reload();
                                } catch (e) {
                                    alert("Failed to reset data.");
                                }
                            }
                        }}
                        className="bg-red-500 hover:bg-red-600 text-white"
                    >
                        Reset Data
                    </Button>
                </div>
            </CardContent>
        </Card>
        
        {success && (
            <div className="fixed bottom-8 right-8 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-6 py-4 rounded-xl backdrop-blur-md shadow-2xl animate-in fade-in slide-in-from-bottom-4">
                <div className="flex items-center space-x-2">
                    <CheckCircle className="h-5 w-5" />
                    <span className="font-medium">Settings saved successfully!</span>
                </div>
            </div>
        )}
      </div>
    </div>
  );
}
