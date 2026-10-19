// ==================== EMPLOYEES ====================

async function getEmployees() {
    return apiGet("/employees/");
}


async function createEmployee(data) {
    const body = {
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        phone: data.phone,
        password: data.password,
        position_id: Number(data.position_id || data.position),
        status: Boolean(data.status)
    };

    return apiPost("/employees/", body);
}


async function updateEmployee(employeeId, data) {
    const body = {
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        phone: data.phone,
        position_id: Number(data.position_id || data.position),
        status: Boolean(data.status)
    };

    if (data.password) {
        body.password = data.password;
    }

    return apiPatch(`/employees/${employeeId}`, body);
}


async function deleteEmployee(employeeId) {
    return apiDelete(`/employees/${employeeId}`);
}


// ==================== POSITIONS ====================

async function getPositions() {
    return apiGet("/positions/");
}


async function createPosition(data) {
    const body = {
        name: data.name,
        description: data.description || null
    };

    return apiPost("/positions/", body);
}


async function updatePosition(positionId, data) {
    const body = {
        name: data.name,
        description: data.description || null
    };

    return apiPatch(`/positions/${positionId}`, body);
}


async function deletePosition(positionId) {
    return apiDelete(`/positions/${positionId}`);
}


// ==================== ROOM CATEGORIES ====================

async function getRoomCategories() {
    return apiGet("/room-categories/");
}


async function createRoomCategory(data) {
    const body = {
        name: data.name,
        description: data.description || null,
        max_guests: Number(data.max_guests),
        price_per_night: Number(data.price_per_night)
    };

    return apiPost("/room-categories/", body);
}


async function updateRoomCategory(categoryId, data) {
    const body = {
        name: data.name,
        description: data.description || null,
        max_guests: Number(data.max_guests),
        price_per_night: Number(data.price_per_night)
    };

    return apiPatch(`/room-categories/${categoryId}`, body);
}


async function deleteRoomCategory(categoryId) {
    return apiDelete(`/room-categories/${categoryId}`);
}


// ==================== ROOMS ====================

async function getAdminRooms() {
    return apiGet("/rooms/");
}


async function createRoom(data) {
    const body = {
        room_number: Number(data.room_number),
        category_id: Number(data.category_id),
        status: data.status || "free"
    };

    return apiPost("/rooms/", body);
}


async function updateRoom(roomId, data) {
    const body = {
        room_number: Number(data.room_number),
        category_id: Number(data.category_id),
        status: data.status
    };

    return apiPatch(`/rooms/${roomId}`, body);
}


async function deleteRoom(roomId) {
    return apiDelete(`/rooms/${roomId}`);
}


// ==================== AUDIT LOGS ====================

async function getAuditLogs(filters = {}) {
    return apiGet("/audit-logs/", {
        employee_id: filters.employee_id,
        table_name: filters.table_name,
        action_type: filters.action_type,
        skip: filters.skip || 0,
        limit: filters.limit || 100
    });
}


// ==================== HELPERS ====================

function formatAdminMoney(value) {
    if (value === null || value === undefined) {
        return "-";
    }

    return `${Number(value).toFixed(2)} руб.`;
}


function formatAdminDateTime(dateValue) {
    if (!dateValue) {
        return "-";
    }

    return new Date(dateValue).toLocaleString("ru-RU");
}


function formatAdminStatus(status) {
    if (status === true) {
        return "Активен";
    }

    if (status === false) {
        return "Неактивен";
    }

    return status || "-";
}


function getAdminStatusClass(status) {
    if (status === true) {
        return "status-badge status-free";
    }

    if (status === false) {
        return "status-badge status-cancelled";
    }

    if (status === "free") {
        return "status-badge status-free";
    }

    if (status === "occupied") {
        return "status-badge status-occupied";
    }

    if (status === "cleaning") {
        return "status-badge status-cleaning";
    }

    if (status === "pending") {
        return "status-badge status-pending";
    }

    if (status === "confirmed") {
        return "status-badge status-confirmed";
    }

    if (status === "completed") {
        return "status-badge status-completed";
    }

    if (status === "cancelled") {
        return "status-badge status-cancelled";
    }

    if (status === "paid") {
        return "status-badge status-paid";
    }

    return "status-badge";
}


function showAdminError(elementId, message) {
    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.textContent = message;
    element.classList.remove("d-none");
}


function hideAdminError(elementId) {
    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.textContent = "";
    element.classList.add("d-none");
}


function showAdminSuccess(elementId, message) {
    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.textContent = message;
    element.classList.remove("d-none");
}


function hideAdminSuccess(elementId) {
    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.textContent = "";
    element.classList.add("d-none");
}


function clearAdminMessages() {
    hideAdminError("errorMessage");
    hideAdminSuccess("successMessage");
}