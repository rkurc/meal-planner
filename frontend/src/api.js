export class ApiError extends Error {
  constructor(message, status, body) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

async function request(method, url, body) {
  const headers = {};
  const opts = { method, headers };
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  const response = await fetch(url, opts);
  if (response.status === 204) {
    if (!response.ok) {
      throw new ApiError(response.statusText, response.status, null);
    }
    return undefined;
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data.error || data.detail || response.statusText;
    throw new ApiError(message, response.status, data);
  }
  return data;
}

export const api = {
  get: (url) => request("GET", url),
  post: (url, body) => request("POST", url, body),
  put: (url, body) => request("PUT", url, body),
  del: (url) => request("DELETE", url),
};
