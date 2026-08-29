// ==================================================
// Profile Match
// search.js
// ==================================================


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
    // ログイン確認
    // ----------------------------------------------

    const token =
        localStorage.getItem("access_token");


    if (!token) {

        alert("ログインしてください");

        window.location.href =
            "login.html";

        return;
    }


    // ----------------------------------------------
    // 現在のユーザーID
    // ----------------------------------------------

    const myUserId =
        currentUserId;


    if (!myUserId) {

        alert(
            "ログイン情報からユーザーIDを取得できませんでした。"
        );

        return;
    }


    console.log(
        "Current User ID:",
        myUserId
    );


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

    messageElement.innerHTML = `
        <div class="message loading">
            検索しています...
        </div>
    `;


    try {

        // ------------------------------------------
        // API
        // ------------------------------------------

        const response =
            await fetch(
                `${API_BASE_URL}/api/users?${params.toString()}`
            );


        console.log(
            "Search API status:",
            response.status
        );


        // ------------------------------------------
        // APIエラー
        // ------------------------------------------

        if (!response.ok) {

            const errorText =
                await response.text();

            console.error(
                "Search API error:",
                errorText
            );

            throw new Error(
                `HTTP ${response.status}`
            );
        }


        const data =
            await response.json();


        console.log(
            "Search result:",
            data
        );


        messageElement.innerHTML = "";


        // ------------------------------------------
        // 自分自身を除外
        // ------------------------------------------

        const users =
            (data.users || []).filter(
                function(user) {

                    return (
                        String(user.user_id) !==
                        String(myUserId)
                    );

                }
            );


        console.log(
            "Users after excluding myself:",
            users
        );


        // ------------------------------------------
        // 件数
        // ------------------------------------------

        resultCountElement.textContent =
            `検索結果：${users.length}人`;


        // ------------------------------------------
        // 0件
        // ------------------------------------------

        if (users.length === 0) {

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

        users.forEach(
            function(user) {

                const card =
                    document.createElement("div");


                card.className =
                    "user-card";


                const hobbies =
                    (user.hobbies || []).join("、");


                card.innerHTML = `

                    <h3>
                        ${escapeHtml(
                            user.name
                        )}
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
                            ${escapeHtml(
                                user.job || ""
                            )}
                        </div>


                        <div>
                            年収：
                            ${user.income}万円
                        </div>


                        <div>
                            地域：
                            ${escapeHtml(
                                user.region || ""
                            )}
                        </div>


                        <div>
                            趣味：
                            ${escapeHtml(
                                hobbies
                            )}
                        </div>

                    </div>


                    <button
                        class="profile-button"
                        onclick="
                            viewProfile(
                                '${escapeHtml(
                                    user.user_id
                                )}'
                            )
                        "
                    >
                        プロフィールを見る
                    </button>


                    <button
                        onclick="
                            bookmarkUser(
                                '${escapeHtml(
                                    user.user_id
                                )}'
                            )
                        "
                    >
                        ♡ ブックマーク
                    </button>

                `;


                resultsElement.appendChild(
                    card
                );

            }
        );


    } catch (error) {

        console.error(
            "Search error:",
            error
        );


        messageElement.innerHTML = `
            <div class="message error">
                検索に失敗しました。<br>
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

    // ----------------------------------------------
    // 自分自身へのブックマーク防止
    // ----------------------------------------------

    if (
        String(targetUserId) ===
        String(currentUserId)
    ) {

        alert(
            "自分自身はブックマークできません。"
        );

        return;
    }


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


        console.log(
            "Bookmark API status:",
            response.status
        );


        if (!response.ok) {

            const errorText =
                await response.text();

            console.error(
                "Bookmark API error:",
                errorText
            );

            throw new Error(
                `HTTP ${response.status}`
            );
        }


        const data =
            await response.json();


        if (data.matched) {

            alert(
                "🎉 マッチングしました！"
            );

        }

        else if (
            data.message ===
            "Already bookmarked"
        ) {

            alert(
                "すでにブックマークしています。"
            );

        }

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
