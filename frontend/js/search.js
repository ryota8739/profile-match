// ==================================================
// 検索
// ==================================================

async function searchUsers() {

    const resultsElement =
        document.getElementById("results");

    const resultCountElement =
        document.getElementById("resultCount");

    const messageElement =
        document.getElementById("message");


    // ----------------------------------------------
    // 初期化
    // ----------------------------------------------

    resultsElement.innerHTML = "";

    resultCountElement.innerHTML = "";

    messageElement.innerHTML = "";


    // ----------------------------------------------
    // 検索条件
    // ----------------------------------------------

    const minAge =
        document.getElementById("minAge").value;

    const maxAge =
        document.getElementById("maxAge").value;

    const minHeight =
        document.getElementById("minHeight").value;

    const maxHeight =
        document.getElementById("maxHeight").value;

    const minIncome =
        document.getElementById("minIncome").value;

    const maxIncome =
        document.getElementById("maxIncome").value;

    const region =
        document.getElementById("region").value;


    // ----------------------------------------------
    // URLパラメータ
    // ----------------------------------------------

    const params =
        new URLSearchParams();


    if (minAge) {

        params.append(
            "min_age",
            minAge
        );

    }


    if (maxAge) {

        params.append(
            "max_age",
            maxAge
        );

    }


    if (minHeight) {

        params.append(
            "min_height",
            minHeight
        );

    }


    if (maxHeight) {

        params.append(
            "max_height",
            maxHeight
        );

    }


    if (minIncome) {

        params.append(
            "min_income",
            minIncome
        );

    }


    if (maxIncome) {

        params.append(
            "max_income",
            maxIncome
        );

    }


    if (region) {

        params.append(
            "region",
            region
        );

    }


    // ----------------------------------------------
    // Loading
    // ----------------------------------------------

    messageElement.innerHTML =
        `<div class="message loading">
            検索しています...
        </div>`;


    try {

        // ------------------------------------------
        // API
        // ------------------------------------------

        const response =
            await fetch(
                `${API_BASE_URL}/api/users?${params.toString()}`
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );

        }


        const data =
            await response.json();


        messageElement.innerHTML = "";


        // ------------------------------------------
        // 件数
        // ------------------------------------------

        resultCountElement.textContent =
            `検索結果：${data.count}人`;


        // ------------------------------------------
        // 0件
        // ------------------------------------------

        if (data.count === 0) {

            resultsElement.innerHTML = `
                <div class="message">
                    条件に一致するユーザーが
                    見つかりませんでした。
                </div>
            `;

            return;
        }


        // ------------------------------------------
        // 結果表示
        // ------------------------------------------

        data.users.forEach(user => {

            const card =
                document.createElement("div");


            card.className =
                "user-card";


            const hobbies =
                (user.hobbies || []).join("、");


            card.innerHTML = `

                <h3>
                    ${escapeHtml(user.name)}
                </h3>


                <div class="user-info">

                    <div>
                        年齢：
                        ${user.age}歳
                    </div>


                    <div>
                        身長：
                        ${user.height}cm
                    </div>


                    <div>
                        職種：
                        ${escapeHtml(user.job || "")}
                    </div>


                    <div>
                        年収：
                        ${user.income}万円
                    </div>


                    <div>
                        地域：
                        ${escapeHtml(user.region || "")}
                    </div>


                    <div>
                        趣味：
                        ${escapeHtml(hobbies)}
                    </div>

                </div>


                <button
                    class="profile-button"
                    onclick="
                        viewProfile('${user.user_id}')
                    "
                >
                    プロフィールを見る
                </button>


                <button
                    onclick="
                        bookmarkUser('${user.user_id}')
                    "
                >
                    ♡ ブックマーク
                </button>

            `;


            resultsElement.appendChild(card);

        });


    } catch (error) {

        console.error(
            "Search error:",
            error
        );


        messageElement.innerHTML = `
            <div class="message error">
                検索に失敗しました。
                APIサーバーとの通信を確認してください。
            </div>
        `;

    }

}


// ==================================================
// ブックマーク
// ==================================================

async function bookmarkUser(
    targetUserId
) {

    try {

        const params =
            new URLSearchParams();


        params.append(
            "user_id",
            currentUserId
        );


        params.append(
            "target_user_id",
            targetUserId
        );


        const response =
            await fetch(
                `${API_BASE_URL}/api/bookmarks?${params.toString()}`,
                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );

        }


        const data =
            await response.json();


        // ------------------------------------------
        // Match成立
        // ------------------------------------------

        if (data.matched) {

            alert(
                "🎉 マッチングしました！"
            );

        }

        // ------------------------------------------
        // すでに登録済み
        // ------------------------------------------

        else if (
            data.message ===
            "Already bookmarked"
        ) {

            alert(
                "すでにブックマークしています。"
            );

        }

        // ------------------------------------------
        // 通常
        // ------------------------------------------

        else {

            alert(
                "♡ ブックマークしました！"
            );

        }


    } catch (error) {

        console.error(
            "Bookmark error:",
            error
        );


        alert(
            "ブックマークに失敗しました。"
        );

    }

}


// ==================================================
// プロフィール
// ==================================================

function viewProfile(
    userId
) {

    location.href =
        `profile.html?id=${encodeURIComponent(userId)}`;

}


// ==================================================
// XSS対策
// ==================================================

function escapeHtml(
    value
) {

    const div =
        document.createElement("div");


    div.textContent =
        value ?? "";


    return div.innerHTML;
}
