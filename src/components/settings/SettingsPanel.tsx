import { useEffect } from "react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Select } from "../ui/select";
import { ScrollArea } from "../ui/scroll-area";
import { ProviderConfig } from "./ProviderConfig";
import { useSettings } from "../../stores/settings";
import { ProviderType } from "../../lib/types";
import { Save, Server, Sliders, Layers, Clock, Check } from "lucide-react";
import { useState } from "react";

const PROVIDER_OPTIONS = [
  { value: "openrouter", label: "OpenRouter" },
  { value: "lm-studio", label: "LM Studio (Local)" },
  { value: "opencode-proxy", label: "OpenCode Proxy" },
];

export function SettingsPanel() {
  const {
    settings, load, loaded, setProvider, setApiKey, setModel, setModels,
    setSearxngUrl, setResearchDepth, setMaxPages, setNumRounds, setTimeLimit, save,
  } = useSettings();
  const [saved, setSaved] = useState(false);

  useEffect(() => { load(); }, [load]);

  if (!loaded || !settings) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="w-5 h-5 rounded-full border-2 border-primary/30 border-t-primary animate-spin" />
      </div>
    );
  }

  const activeConfig = settings.providers[settings.provider];

  const handleSave = async () => {
    await save();
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <ScrollArea className="h-full">
      <div className="max-w-2xl mx-auto p-6 space-y-5">
        <div>
          <h1 className="text-base font-semibold">Settings</h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            Configure your LLM provider and research parameters.
          </p>
        </div>

        <section className="panel">
          <div className="panel-header">
            <div className="flex items-center gap-2">
              <Server className="w-3.5 h-3.5 text-primary" />
              <span className="section-title">LLM Provider</span>
            </div>
          </div>
          <div className="p-4 space-y-4">
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">Provider</Label>
              <Select
                value={settings.provider}
                onChange={(e) => setProvider(e.target.value as ProviderType)}
                options={PROVIDER_OPTIONS}
                className="w-full"
              />
            </div>
            <ProviderConfig
              type={settings.provider}
              config={activeConfig}
              onApiKeyChange={(key) => setApiKey(settings.provider, key)}
              onModelChange={(model) => setModel(settings.provider, model)}
              onModelsChange={(models) => setModels(settings.provider, models)}
            />
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div className="flex items-center gap-2">
              <Sliders className="w-3.5 h-3.5 text-primary" />
              <span className="section-title">Research Parameters</span>
            </div>
          </div>
          <div className="p-4 border-b border-border/50">
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">SearXNG URL (optional fallback search)</Label>
              <Input
                type="text"
                placeholder="http://localhost:8080"
                value={settings.searxngUrl}
                onChange={(e) => setSearxngUrl(e.target.value)}
                className="h-9 text-sm"
              />
              <p className="text-[10px] text-muted-foreground">
                When DuckDuckGo returns too few results, falls back to self-hosted SearXNG
              </p>
            </div>
          </div>
          <div className="p-4">
            <div className="grid grid-cols-4 gap-4">
              <div className="space-y-1.5">
                <Label className="text-xs text-muted-foreground">Depth</Label>
                <Input
                  type="number"
                  min={1}
                  max={15}
                  value={settings.researchDepth}
                  onChange={(e) => setResearchDepth(Number(e.target.value))}
                  className="h-9 text-sm"
                />
                <p className="text-[10px] text-muted-foreground">Gap-fill iterations (1–15)</p>
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs text-muted-foreground">Pages / Query</Label>
                <Input
                  type="number"
                  min={1}
                  max={50}
                  value={settings.maxPagesPerQuery}
                  onChange={(e) => setMaxPages(Number(e.target.value))}
                  className="h-9 text-sm"
                />
                <p className="text-[10px] text-muted-foreground">Results per search (1–50)</p>
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs text-muted-foreground flex items-center gap-1">
                  <Layers className="w-3 h-3" />
                  Rounds
                </Label>
                <Input
                  type="number"
                  min={1}
                  max={10}
                  value={settings.numRounds}
                  onChange={(e) => setNumRounds(Number(e.target.value))}
                  className="h-9 text-sm"
                />
                <p className="text-[10px] text-muted-foreground">Pipeline passes (1–10)</p>
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs text-muted-foreground flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  Time Limit
                </Label>
                <Input
                  type="number"
                  min={5}
                  max={120}
                  value={settings.timeLimitMinutes}
                  onChange={(e) => setTimeLimit(Number(e.target.value))}
                  className="h-9 text-sm"
                />
                <p className="text-[10px] text-muted-foreground">Max minutes (5–120)</p>
              </div>
            </div>
          </div>
        </section>

        <div className="flex justify-end">
          <Button onClick={handleSave} className="gap-1.5 min-w-[100px]">
            {saved ? <Check className="w-3.5 h-3.5" /> : <Save className="w-3.5 h-3.5" />}
            {saved ? "Saved" : "Save Settings"}
          </Button>
        </div>
      </div>
    </ScrollArea>
  );
}
