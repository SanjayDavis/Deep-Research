import { useState, useCallback, useMemo } from "react";
import { SearchableSelect } from "../ui/searchable-select";
import { Button } from "../ui/button";
import { Loader2, Check, AlertCircle, Sparkles, Plug, RefreshCw } from "lucide-react";
import { ProviderType, ProviderConfig } from "../../lib/types";
import { fetchModels } from "../../lib/api";

interface ModelSelectorProps {
  providerType: ProviderType;
  config: ProviderConfig;
  onModelChange: (model: string) => void;
  onModelsChange: (models: string[]) => void;
}

const PROVIDER_HINTS: Record<ProviderType, string> = {
  openrouter: "Enter your OpenRouter API key, then click Connect",
  "lm-studio": "Make sure LM Studio is running, then click Connect",
  "opencode-proxy": "Make sure the proxy is running, then click Connect",
};

function cleanModelName(name: string): string {
  let cleaned = name;
  cleaned = cleaned.replace(/^.*[\/\\]/, "");
  cleaned = cleaned.replace(/\.(gguf|bin|pt|pth)$/i, "");
  cleaned = cleaned.replace(/-\d+[bk]_[a-z0-9_-]+$/i, "");
  cleaned = cleaned.replace(/lm-studio\//i, "");
  return cleaned;
}

export function ModelSelector({ providerType, config, onModelChange, onModelsChange }: ModelSelectorProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleFetch = useCallback(async (isRefresh: boolean) => {
    const needsKey = providerType === "openrouter";
    if (needsKey && (!config.apiKey || config.apiKey.length < 8)) {
      setError("Enter a valid API key first");
      return;
    }
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      const models = await fetchModels(config.baseUrl, config.apiKey);
      if (models.length === 0) {
        setError(providerType === "lm-studio"
          ? "LM Studio returned no models. Make sure you have loaded a model in LM Studio first."
          : "No models returned from the provider.");
        return;
      }
      const currentModel = config.model;
      onModelsChange(models);
      setSuccess(`${models.length} models available`);
      if (!isRefresh && models.length > 0 && !currentModel) {
        onModelChange(models[0]);
      } else if (!isRefresh && models.length > 0 && !models.includes(currentModel)) {
        onModelChange(models[0]);
      }
    } catch (err) {
      const msg = String(err);
      if (providerType === "lm-studio" && (msg.includes("Connection failed") || msg.includes("refused"))) {
        setError("Could not connect to LM Studio. Make sure it is running on port 1234.");
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  }, [config.baseUrl, config.apiKey, config.model, providerType, onModelChange, onModelsChange]);

  const handleConnect = useCallback(() => handleFetch(false), [handleFetch]);
  const handleRefresh = useCallback(() => handleFetch(true), [handleFetch]);

  const modelOptions = useMemo(() => {
    return (config.models ?? []).map((m) => {
      const display = providerType === "lm-studio" ? cleanModelName(m) : m;
      const searchTerms = [m, display].filter((s) => s !== m);
      return { value: m, label: display, searchTerms };
    });
  }, [config.models, providerType]);

  const hasModels = config.models && config.models.length > 0;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
          <Sparkles className="w-3 h-3" />
          Model
        </label>
        <div className="flex items-center gap-1">
          {hasModels && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRefresh}
              disabled={loading}
              className="h-7 w-7 p-0"
              aria-label="Refresh model list"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            </Button>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={handleConnect}
            disabled={loading}
            className="h-7 text-xs gap-1.5"
          >
            {loading ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Plug className="w-3.5 h-3.5" />
            )}
            {loading ? "Connecting..." : hasModels ? "Reconnect" : "Connect"}
          </Button>
        </div>
      </div>

      {hasModels ? (
        <SearchableSelect
          options={modelOptions}
          value={config.model}
          onChange={onModelChange}
          placeholder="Search and select a model..."
        />
      ) : (
        <div className="flex items-center gap-2 px-3 py-2.5 rounded-md bg-secondary/50 text-xs text-muted-foreground">
          <AlertCircle className="w-3.5 h-3.5 shrink-0" />
          <span>{PROVIDER_HINTS[providerType]}</span>
        </div>
      )}

      {loading && (
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Loader2 className="w-3 h-3 animate-spin" />
          Connecting to {config.baseUrl}...
        </div>
      )}
      {error && (
        <div className="flex items-start gap-1.5 text-xs text-stage-error">
          <AlertCircle className="w-3 h-3 mt-0.5 shrink-0" />
          <span>{error}</span>
        </div>
      )}
      {success && (
        <div className="flex items-center gap-1.5 text-xs text-stage-done">
          <Check className="w-3 h-3" />
          {success}
        </div>
      )}
    </div>
  );
}