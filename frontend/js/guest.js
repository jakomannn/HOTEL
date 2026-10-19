function toApiDate(dateValue) {
    if (!dateValue) {
        return null;
    }

    if (dateValue.includes("T")) {
        return dateValue;
    }

    return `${dateValue}T00:00:00`;
}


async function getAvailableRooms(checkInDate, checkOutDate, categoryId = null) {
    return apiGet("/reservations/available-rooms", {
        check_in_date: toApiDate(checkInDate),
        check_out_date: toApiDate(checkOutDate),
        category_id: categoryId
    });
}


async function createGuestReservation(data) {
    const body = {
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        phone: data.phone,
        passport_number: data.passport_number,
        room_id: Number(data.room_id),
        check_in_date: toApiDate(data.check_in_date),
        check_out_date: toApiDate(data.check_out_date)
    };

    const result = await apiPost("/reservations/guest", body);

    saveGuestPhone(data.phone);
    saveGuestReservationResult(result);

    return result;
}


async function getGuestReservationsByPhone(phone) {
    const normalizedPhone = String(phone || "").trim();

    if (!normalizedPhone) {
        throw new Error("Введите номер телефона");
    }

    saveGuestPhone(normalizedPhone);

    return apiPost("/reservations/guest/by-phone", {
        phone: normalizedPhone
    });
}


async function payReservation(paymentId) {
    return apiPatch(`/payments/${paymentId}/paid`);
}


function saveGuestReservationResult(result) {
    if (!result) {
        return;
    }

    if (result.reservation) {
        localStorage.setItem(
            "guest_reservation",
            JSON.stringify(result.reservation)
        );
    }

    if (result.payment) {
        localStorage.setItem(
            "guest_payment",
            JSON.stringify(result.payment)
        );
    }
}


function getSavedGuestReservation() {
    const value = localStorage.getItem("guest_reservation");

    if (!value) {
        return null;
    }

    try {
        return JSON.parse(value);
    } catch (error) {
        return null;
    }
}


function getSavedGuestPayment() {
    const value = localStorage.getItem("guest_payment");

    if (!value) {
        return null;
    }

    try {
        return JSON.parse(value);
    } catch (error) {
        return null;
    }
}


function saveGuestPhone(phone) {
    if (!phone) {
        return;
    }

    localStorage.setItem("guest_phone", phone);
}


function getSavedGuestPhone() {
    return localStorage.getItem("guest_phone");
}


function clearSavedGuestReservation() {
    localStorage.removeItem("guest_reservation");
    localStorage.removeItem("guest_payment");
}


function clearSavedGuestData() {
    localStorage.removeItem("guest_reservation");
    localStorage.removeItem("guest_payment");
    localStorage.removeItem("guest_phone");
}


function formatDate(dateValue) {
    if (!dateValue) {
        return "-";
    }

    return new Date(dateValue).toLocaleDateString("ru-RU");
}


function formatDateTime(dateValue) {
    if (!dateValue) {
        return "-";
    }

    return new Date(dateValue).toLocaleString("ru-RU");
}


function formatMoney(value) {
    if (value === null || value === undefined) {
        return "-";
    }

    return `${Number(value).toFixed(2)} руб.`;
}


function getStatusClass(status) {
    if (!status) {
        return "status-badge";
    }

    return `status-badge status-${status}`;
}


function showGuestError(elementId, message) {
    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.textContent = message;
    element.classList.remove("d-none");
}


function hideGuestError(elementId) {
    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.textContent = "";
    element.classList.add("d-none");
}


function showGuestSuccess(elementId, message) {
    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.textContent = message;
    element.classList.remove("d-none");
}


function hideGuestSuccess(elementId) {
    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.textContent = "";
    element.classList.add("d-none");
}