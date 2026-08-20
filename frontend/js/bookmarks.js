async function loadBookmarks() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/api/bookmarks?user_id=${encodeURIComponent(currentUserId)}`
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );

        }


        const data =
            await response.json();


        const results =
            document.getElementById(
                "results"
            );


        results.innerHTML = "";


        // ------------------------------------------
        // ブックマークがない場合
        // ------------------------------------------

        if (data.count === 0) {

            results.innerHTML =
                "<p>ブックマークはありません。</p>";

            return;
        }


        // ------------------------------------------
        // ブックマーク一覧
        // ------------------------------------------

        data.users.forEach(user => {

            const div =
                document.createElement(
                    "div"
                );


            div.innerHTML = `

                <h3>
                    ${escapeHtml(user.name)}
                </h3>

                <p>
                    ${user.age}歳 /
                    ${user.height}cm
                </p>

                <p>
                    ${escapeHtml(user.job || "")}
                </p>

                <p>
                    ${user.income}万円
                </p>

                <p>
                    ${escapeHtml(user.region || "")}
                </p>

                <p>
                    趣味：
                    ${escapeHtml(
                        (user.hobbies || []).join("、")
                    )}
                </p>

                <button
                    onclick="
                        deleteBookmark('${user.user_id}')
                    "
                >
                    ブックマーク解除
                </button>

                <hr>

            `;


            results.appendChild(div);

        });


    } catch (error) {

        console.error(
            "Bookmark loading error:",
            error
        );


        document.getElementById(
            "results"
        ).innerHTML =
            "<p>ブックマークの取得に失敗しました。</p>";

    }

}


// ==================================================
// ブックマーク解除
// ==================================================

async function deleteBookmark(
    targetUserId
) {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/api/bookmarks/${encodeURIComponent(targetUserId)}?user_id=${encodeURIComponent(currentUserId)}`,
                {
                    method: "DELETE"
                }
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );

        }


        alert(
            "ブックマークを解除しました。"
        );


        // 一覧を再読み込み

        await loadBookmarks();


    } catch (error) {

        console.error(
            "Bookmark delete error:",
            error
        );


        alert(
            "ブックマーク解除に失敗しました。"
        );

    }

}


// ==================================================
// XSS対策
// ==================================================

function escapeHtml(value) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        value ?? "";


    return div.innerHTML;
}


// ==================================================
// ページ読み込み時に実行
// ==================================================

loadBookmarks();
