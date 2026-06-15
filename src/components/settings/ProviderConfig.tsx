import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { ModelSelector } from "./ModelSelector";
import { ProviderType, ProviderConfig as ProviderConfigType } from "../../lib/types";

interface ProviderConfigProps {
  type: ProviderType;
  config: ProviderConfigType;
  onApiKeyChange: (key: string) => void;
  onModelChange: (model: string) => void;
  onModelsChange: (models: string[]) => void;
}

export function ProviderConfig({ type, config, onApiKeyChange, onModelChange, onModelsChange }: ProviderConfigProps) {
  return (
    <div className="space-y-3">
      <div className="space-y-1.5">
        <Label className="text-xs text-muted-foreground">API Endpoint</Label>
        <Input
          value={config.baseUrl}
          readOnly
          className="text-xs font-mono text-muted-foreground bg-secondary/30 select-all"
          onClick={(e) => (e.target as HTMLInputElement).select()}
        />
      </div>

      <div className="space-y-1.5">
        <Label className="text-xs text-muted-foreground">API Key</Label>
        <Input
          type="password"
          value={config.apiKey}
          onChange={(e) => onApiKeyChange(e.target.value)}
          placeholder={type === "openrouter" ? "sk-or-..." : type === "lm-studio" ? "Leave empty for local" : "Leave empty for proxy"}
          className="font-mono text-xs"
        />
      </div>

      <ModelSelector
        providerType={type}
        config={config}
        onModelChange={onModelChange}
        onModelsChange={onModelsChange}
      />
    </div>
  );
}
