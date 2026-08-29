// ==================================================
// Profile Match
// common.js
// ==================================================


// ==================================================
// API
// ==================================================

const API_BASE_URL =
    "http://13.115.204.216:8000";


// ==================================================
// JWTから現在のユーザーIDを取得
// ==================================================

function getCurrentUserId() {

    const token =
        localStorage.getItem("access_token");


    if (!token) {

        return null;

    }


    try {

        const parts =
            token.split(".");


        if (parts.length !== 3) {

            return null;

        }


        // Base64URL → Base64

        let payload =
            parts[1]
                .replace(/-/g, "+")
                .replace(/_/g, "/");


        // padding

        while (
            payload.length % 4 !== 0
        ) {

            payload += "=";

        }


        const decoded =
            JSON.parse(
                atob(payload)
            );


        return (
            decoded.user_id ||
            decoded.sub ||
            null
        );


    } catch (error) {

        console.error(
            "JWT decode error:",
            error
        );


        return null;

    }

}


// ==================================================
// 現在のユーザーID
// ==================================================

const currentUserId =
    getCurrentUserId();

