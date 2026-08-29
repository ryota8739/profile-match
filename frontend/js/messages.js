// ================================================
// Profile Match
// messages.js
// ================================================


// ================================================
// API URL
// ================================================

const API_URL = API_BASE_URL;


// ================================================
// 初期処理
// ================================================

document.addEventListener("DOMContentLoaded", function () {

    loadMatches();

});


// ================================================
// マッチ一覧取得
// ================================================

async function loadMatches() {

    const token =
        localStorage.getItem("access_token");


    // --------------------------------------------
    // ログイン確認
    // --------------------------------------------

    if (!token) {

        alert("ログインしてください");

        window.location.href =
            "login.html";

        return;
    }


    try {

        // ----------------------------------------
        // 現在のユーザーID
        // common.jsのcurrentUserIdを使用
        // ----------------------------------------

        const response =
            await fetch(
                `${API_URL}/api/matches?user_id=${encodeURIComponent(currentUserId)}`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        if (!response.ok) {

            const errorText =
                await response.text();

            console.error(
                "API Error:",
                errorText
            );

            throw new Error(
                "マッチ一覧の取得に失敗しました"
            );
        }


        const data =
            await response.json();


        console.log(
            "Matches:",
            data
        );


        displayMatches(
            data.matches
        );


    } catch (error) {

        console.error(
            error
        );

        document.getElementById(
            "matchList"
        ).innerHTML = `
            <div class="empty">
                マッチ一覧を取得できませんでした。
            </div>
        `;
    }
}


// ================================================
// マッチ一覧表示
// ================================================

function displayMatches(matches) {

    const container =
        document.getElementById(
            "matchList"
        );


    container.innerHTML = "";


    if (!matches || matches.length === 0) {

        container.innerHTML = `
            <div class="empty">
                まだマッチした相手はいません。
            </div>
        `;

        return;
    }


    matches.forEach(function (match) {

        const item =
            document.createElement("div");


        item.className =
            "match-item";


        const name =
            match.name ||
            "名前未設定";


        const details = [];


        if (
            match.age !== null &&
            match.age !== undefined
        ) {

            details.push(
                `${match.age}歳`
            );
        }


        if (
            match.height !== null &&
            match.height !== undefined
        ) {

            details.push(
                `${match.height}cm`
            );
        }


        if (match.region) {

            details.push(
                match.region
            );
        }


        item.innerHTML = `

            <div class="avatar">
                ${escapeHtml(
                    name.charAt(0)
                )}
            </div>

            <div class="user-info">

                <div class="user-name">
                    ${escapeHtml(name)}
                </div>

                <div class="user-detail">
                    ${escapeHtml(
                        details.join(" / ")
                    )}
                </div>

            </div>

        `;


        // ----------------------------------------
        // チャット画面へ
        // ----------------------------------------

        item.addEventListener(
            "click",
            function () {

                openChat(
                    match.match_id,
                    match.user_id,
                    match.name
                );

            }
        );


        container.appendChild(
            item
        );

    });
}


// ================================================
// チャット画面へ移動
// ================================================

function openChat(
    matchId,
    userId,
    name
) {

    const url =
        `chat.html?match_id=${encodeURIComponent(matchId)}` +
        `&user_id=${encodeURIComponent(userId)}` +
        `&name=${encodeURIComponent(name || "")}`;


    window.location.href =
        url;
}


// ================================================
// XSS対策
// ================================================

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";
    }


    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
