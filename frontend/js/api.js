const API_BASE_URL = "http://127.0.0.1:8000";


function getToken() {
    return localStorage.getItem("access_token");
}


function setToken(token) {
    localStorage.setItem("access_token", token);
}


function removeToken() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_role");
}


function getUserRole() {
    return localStorage.getItem("user_role");
}


function setUserRole(role) {
    localStorage.setItem("user_role", role);
}


function buildQueryParams(params = {}) {
    const searchParams = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
        if (
            value !== undefined &&
            value !== null &&
            value !== ""
        ) {
            searchParams.append(key, value);
        }
    });

    const queryString = searchParams.toString();

    return queryString ? `?${queryString}` : "";
}


async function apiRequest(endpoint, options = {}) {
    const token = getToken();

    const headers = {
        ...(options.headers || {})
    };

    const hasBody = options.body !== undefined && options.body !== null;
    const hasContentType = Object.keys(headers).some(
        key => key.toLowerCase() === "content-type"
    );

    if (
        hasBody &&
        !hasContentType &&
        !(options.body instanceof FormData) &&
        !(options.body instanceof URLSearchParams)
    ) {
        headers["Content-Type"] = "application/json";
    }

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers
    });

    let data = null;

    const contentType = response.headers.get("content-type");

    if (contentType && contentType.includes("application/json")) {
        data = await response.json();
    }

    if (!response.ok) {
        const message =
            data?.detail ||
            data?.message ||
            `Ошибка запроса: ${response.status}`;

        throw new Error(
            typeof message === "string"
                ? message
                : JSON.stringify(message)
        );
    }

    return data;
}


async function apiGet(endpoint, params = {}) {
    const queryString = buildQueryParams(params);

    return apiRequest(`${endpoint}${queryString}`, {
        method: "GET"
    });
}


async function apiPost(endpoint, body = {}) {
    return apiRequest(endpoint, {
        method: "POST",
        body: JSON.stringify(body)
    });
}


async function apiPatch(endpoint, body = {}) {
    return apiRequest(endpoint, {
        method: "PATCH",
        body: JSON.stringify(body)
    });
}


async function apiPut(endpoint, body = {}) {
    return apiRequest(endpoint, {
        method: "PUT",
        body: JSON.stringify(body)
    });
}


async function apiDelete(endpoint) {
    return apiRequest(endpoint, {
        method: "DELETE"
    });
}


async function login(email, password) {
    const formData = new URLSearchParams();

    formData.append("username", email);
    formData.append("password", password);

    const response = await apiRequest("/auth/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: formData
    });

    setToken(response.access_token);

    const currentUser = await loadCurrentUser();

    return {
        token: response.access_token,
        user: currentUser
    };
}


async function loadCurrentUser() {
    const user = await apiGet("/auth/me");

    if (user.role) {
        setUserRole(user.role);
    }

    return user;
}


function logout() {
    removeToken();
    window.location.href = "/login.html";
}


function requireAuth() {
    const token = getToken();

    if (!token) {
        window.location.href = "/login.html";
        return false;
    }

    return true;
}


function requireRole(allowedRoles = []) {
    const role = getUserRole();

    if (!role || !allowedRoles.includes(role)) {
        alert("Недостаточно прав для доступа к странице");
        window.location.href = "/login.html";
        return false;
    }

    return true;
}