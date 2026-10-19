async function loginEmployee(email, password) {
    return await login(email, password);
}


function isAuthenticated() {
    return Boolean(getToken());
}


function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = "/login.html";
        return false;
    }

    return true;
}


function requireRole(allowedRoles) {
    if (!requireAuth()) {
        return false;
    }

    const role = getUserRole();

    if (!role || !allowedRoles.includes(role)) {
        alert("Нет доступа к этой странице");
        window.location.href = "/index.html";
        return false;
    }

    return true;
}


function redirectByRole() {
    const role = getUserRole();

    if (role === "admin") {
        window.location.href = "/admin/employees.html";
        return;
    }

    if (role === "manager") {
        window.location.href = "/manager/reservations.html";
        return;
    }

    window.location.href = "/index.html";
}