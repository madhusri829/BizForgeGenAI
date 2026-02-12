class API {
    constructor() {
        this.baseUrl = "/api";
    }

    async request(url, method = "GET", body = null, headers = {}) {
        const config = {
            method,
            headers: {
                "Content-Type": "application/json",
                ...headers
            }
        };

        if (body) {
            config.body = JSON.stringify(body);
        }

        const response = await fetch(url, config);
        return response.json();
    }

    async generateBrand(description, keywords) {
        return this.request(`${this.baseUrl}/generate-brand`, "POST", { description, keywords });
    }

    async saveItem(item_type, content) {
        return this.request(`${this.baseUrl}/save-item`, "POST", { item_type, content });
    }

    async getSavedItems() {
        return this.request(`${this.baseUrl}/saved-items`, "GET");
    }
}

const api = new API();
