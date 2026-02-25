export type Dict = Record<string, unknown>;

export interface FrappeMethodResponse<T> {
  message: T;
}

export interface UIBridgeAppConfig {
  name?: string;
  app_id: string;
  enabled: number;
  auth_mode?: string;
  api_base?: string;
  assets_base?: string;
  default_layout?: string;
  default_layout_preset?: string;
  default_theme?: string;
  navigation_profile?: string;
  base_urls?: Dict;
  feature_flags?: Dict;
  branding?: Dict;
  allowed_origins?: string[];
}

export interface UIBridgeBundle {
  app_id: string;
  hash: string;
  theme: {
    mode: string;
    css_tokens: string;
    hash: string;
  };
  flags: Dict;
  layout: Dict;
  navigation: Dict;
  app_config: UIBridgeAppConfig;
  env: {
    site: string;
    user: string;
    is_system_user: 1;
  };
}

export interface RegistryCallParams {
  mode?: "list" | "get";
  fields?: string[];
  filters?: Dict | unknown[];
  order_by?: string;
  start?: number;
  page_length?: number;
  name?: string;
}

export interface RegistryCallResult {
  ok: 1;
  error: null;
  key: string;
  mode: "list" | "get";
  result: Dict;
}

export interface GalaxyUIClientOptions {
  siteUrl: string;
  cookie?: string;
  defaultHeaders?: Record<string, string>;
}

export class GalaxyUIClient {
  private siteUrl: string;
  private cookie?: string;
  private defaultHeaders: Record<string, string>;

  constructor(options: GalaxyUIClientOptions) {
    this.siteUrl = options.siteUrl.replace(/\/$/, "");
    this.cookie = options.cookie;
    this.defaultHeaders = options.defaultHeaders || {};
  }

  private async callMethod<T>(method: string, args?: Dict): Promise<T> {
    const url = `${this.siteUrl}/api/method/${method}`;
    const body = new URLSearchParams();

    Object.entries(args || {}).forEach(([k, v]) => {
      if (v === undefined || v === null) return;
      body.append(k, typeof v === "string" ? v : JSON.stringify(v));
    });

    const headers: Record<string, string> = {
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      ...this.defaultHeaders,
    };

    if (this.cookie) {
      headers.Cookie = this.cookie;
    }

    const res = await fetch(url, {
      method: "POST",
      headers,
      body,
      credentials: "include",
    });

    if (!res.ok) {
      const txt = await res.text();
      throw new Error(`Frappe method failed (${res.status}): ${txt}`);
    }

    const json = (await res.json()) as FrappeMethodResponse<T>;
    return json.message;
  }

  getUIAppConfig(appId: string): Promise<UIBridgeAppConfig> {
    return this.callMethod<UIBridgeAppConfig>("galaxy_ui.api.bridge.get_ui_app_config", { app_id: appId });
  }

  getUIBundle(appId: string): Promise<UIBridgeBundle> {
    return this.callMethod<UIBridgeBundle>("galaxy_ui.api.bridge.get_ui_bundle", { app_id: appId });
  }

  getUINav(appId?: string): Promise<Dict> {
    return this.callMethod<Dict>("galaxy_ui.api.bridge.get_ui_nav", { app_id: appId || "" });
  }

  callRegistry(key: string, params: RegistryCallParams): Promise<RegistryCallResult> {
    return this.callMethod<RegistryCallResult>("galaxy_ui.api.registry.call", {
      key,
      params,
    });
  }

  getRegistryTypes(appId?: string, key?: string): Promise<Dict> {
    return this.callMethod<Dict>("galaxy_ui.api.registry.types", {
      app_id: appId || "",
      key: key || "",
    });
  }

  getTemplates(templateType?: "dashboard" | "list" | "form"): Promise<Dict[]> {
    return this.callMethod<Dict[]>("galaxy_ui.api.builder.list_templates", {
      template_type: templateType || "",
    });
  }
}
