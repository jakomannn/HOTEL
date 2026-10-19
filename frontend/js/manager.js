async function getCurrentEmployeeId() {
    const user = await loadCurrentUser();

    if (!user || !user.employee_id) {
        throw new Error("Не удалось определить текущего сотрудника");
    }

    return user.employee_id;
}


async function getReservations() {
    return apiGet("/reservations/");
}


async function getReservationById(reservationId) {
    return apiGet(`/reservations/${reservationId}`);
}


async function cancelReservation(reservationId) {
    return apiPatch(`/reservations/${reservationId}/cancel`);
}


async function getClients() {
    return apiGet("/clients/");
}


async function getPayments() {
    return apiGet("/payments/");
}


async function getPaymentById(paymentId) {
    return apiGet(`/payments/${paymentId}`);
}


async function getPaymentsByReservation(reservationId) {
    return apiGet(`/payments/reservation/${reservationId}`);
}


async function confirmPayment(paymentId) {
    return apiPatch(`/payments/${paymentId}/paid`);
}


async function failPayment(paymentId) {
    return apiPatch(`/payments/${paymentId}/failed`);
}


async function getRooms() {
    return apiGet("/rooms/");
}


async function getRoomsByStatus(status) {
    return apiGet(`/rooms/status/${status}`);
}


async function getRoomsByCategory(categoryId) {
    return apiGet(`/rooms/category/${categoryId}`);
}


async function markRoomFree(roomId) {
    return apiPatch(`/rooms/${roomId}/mark-free`);
}


async function getCheckIns() {
    return apiGet("/check-ins/");
}


async function getCheckInsByReservation(reservationId) {
    return apiGet(`/check-ins/reservation/${reservationId}`);
}


async function getCheckInsByEmployee(employeeId) {
    return apiGet(`/check-ins/employee/${employeeId}`);
}


async function checkInReservation(reservationId) {
    const employeeId = await getCurrentEmployeeId();

    const body = {
        reservation_id: Number(reservationId),
        employee_id: Number(employeeId)
    };

    return apiPost("/check-ins/", body);
}


async function checkOut(checkInId, checkOutTime = null) {
    const body = {};

    if (checkOutTime) {
        body.check_out_time = checkOutTime;
    }

    return apiPatch(`/check-ins/${checkInId}/check-out`, body);
}


async function getStayHistory() {
    return apiGet("/stay-history/");
}


async function getStayHistoryByClient(clientId) {
    return apiGet(`/stay-history/client/${clientId}`);
}


async function getStayHistoryByRoom(roomId) {
    return apiGet(`/stay-history/room/${roomId}`);
}


async function getStayHistoryByReservation(reservationId) {
    return apiGet(`/stay-history/reservation/${reservationId}`);
}


async function getStayHistoryByCheckIn(checkInId) {
    return apiGet(`/stay-history/check-in/${checkInId}`);
}


function formatDateTime(dateValue) {
    if (!dateValue) {
        return "-";
    }

    return new Date(dateValue).toLocaleString("ru-RU");
}


function formatDate(dateValue) {
    if (!dateValue) {
        return "-";
    }

    return new Date(dateValue).toLocaleDateString("ru-RU");
}


function formatManagerMoney(value) {
    if (value === null || value === undefined) {
        return "-";
    }

    return `${Number(value).toFixed(2)} руб.`;
}


function getManagerStatusClass(status) {
    if (!status) {
        return "status-badge";
    }

    return `status-badge status-${status}`;
}


function showManagerError(elementId, message) {
    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.textContent = message;
    element.classList.remove("d-none");
}


function hideManagerError(elementId) {
    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.textContent = "";
    element.classList.add("d-none");
}


function showManagerSuccess(elementId, message) {
    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.textContent = message;
    element.classList.remove("d-none");
}


function hideManagerSuccess(elementId) {
    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.textContent = "";
    element.classList.add("d-none");
}


function clearManagerMessages() {
    hideManagerError("errorMessage");
    hideManagerSuccess("successMessage");
}