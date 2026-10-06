const API_BASE = "http://127.0.0.1:8000";
let currentUser = null;
window.onload = function () {
    const popup = document.getElementById("registerPopup");

    // Handle login persistence
    const savedUser = localStorage.getItem("currentUser");
    if (savedUser) {
        currentUser = JSON.parse(savedUser);

        document.getElementById("landing").style.display = "none";
        document.getElementById("navbar").classList.remove("hidden");
        document.getElementById("navUsername").innerText = currentUser.username;

        showSection("profile");
        return;
    }

    // Handle register popup
    if (sessionStorage.getItem("justRegistered") === "true") {
        popup.classList.add("active");
    } else {
        popup.classList.remove("active");
    }
};


/* ---------- REGISTER ---------- */
function register() {
    fetch(`${API_BASE}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            username: registerUsername.value,
            email: registerEmail.value,
            password: registerPassword.value
        })
    })
    .then(res => res.json())
.then(data => {
    // THIS LINE WAS THE MISSING / NON-FIRING PART
    document.getElementById("registerPopup").classList.add("active");


});

}



/* ---------- CLOSE POPUP ---------- */
function closeRegisterPopup() {
   document.getElementById("registerPopup").classList.remove("active");

    // CLEAR REGISTER FORM
    registerUsername.value = "";
    registerEmail.value = "";
    registerPassword.value = "";
}


/* ---------- LOGIN ---------- */
/* ---------- LOGIN ---------- */
function login() {
    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;

    fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }

        
        currentUser = data;
localStorage.setItem("currentUser", JSON.stringify(data));


        // Hide landing
        document.getElementById("landing").style.display = "none";

        // Show navbar
        document.getElementById("navbar").classList.remove("hidden");

        // Show username
        document.getElementById("navUsername").innerText = data.username;

        // Go to profile
        showSection("profile");

        // 🔥 IMPORTANT
        loadMyPosts();   // My posts in profile
        loadFeed();      // Feed (others posts)
        loadPendingComments();

    });
}


/* ---------- NAVIGATION ---------- */
function showSection(id) {
    document.querySelectorAll(".section").forEach(sec =>
        sec.classList.add("hidden")
    );
    document.getElementById(id).classList.remove("hidden");

    if (id === "notifications") {
        loadNotifications();   // 🔥 THIS WAS MISSING
    }

    if (id === "profile") {
        loadMyPosts();
        loadPendingComments();
    }

    if (id === "feed") {
        loadFeed();
    }
}


/* ---------- LOGOUT ---------- */
function logout() {
    localStorage.removeItem("currentUser");
    location.reload();
}

function showAIPopup(data) {
    const popup = document.getElementById("aiPopup");
    const box = document.getElementById("aiPopupBox");

    document.getElementById("aiTitle").innerText =
        data.status === "approved"
            ? "✅ Comment is Non-Toxic"
            : "⚠️ Toxic Comment Detected";

    document.getElementById("aiCategory").innerText =
        "Category: " + data.toxicity_type;

    document.getElementById("aiConfidence").innerText =
        "Confidence: " + Math.round(data.toxicity_score * 100) + "%";

    document.getElementById("aiMessage").innerText = data.message;

    box.className = "popup-box " + (data.status === "approved" ? "safe" : "toxic");

    popup.classList.add("active");   // ✅ IMPORTANT
}

function closeAIPopup() {
    document.getElementById("aiPopup").classList.remove("active");
}

/* ---------- SUBMIT COMMENT ---------- */
function submitComment(postId) {
    const input = document.getElementById(`comment-${postId}`);
    const text = input.value;

    if (!text || !text.trim()) {
        alert("Comment cannot be empty");
        return;
    }

    fetch(`${API_BASE}/comments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            post_id: postId,
            user_id: currentUser.user_id,
            text: text
        })
    })
    .then(res => res.json())
    .then(data => {
        showAIPopup(data);
        input.value = "";

        if (data.status === "approved") {
            loadFeed();
        }
    })
    .catch(err => {
        console.error(err);
        alert("Failed to submit comment");
    });
}

/* ---------- LOAD FEED ---------- */
function loadFeed() {
    fetch(`${API_BASE}/feed`)
        .then(res => res.json())
        .then(posts => {
            const container = document.getElementById("feedContainer");
            container.innerHTML = "";

            if (!posts || posts.length === 0) {
                container.innerHTML = "<p>No posts available</p>";
                return;
            }

            posts.forEach(post => {
                const div = document.createElement("div");

                div.style.border = "1px solid #ccc";
                div.style.padding = "15px";
                div.style.marginBottom = "15px";
                div.style.background = "white";
                div.style.color = "black";
                div.style.borderRadius = "6px";

                div.innerHTML = `
                    <strong>${post.username}</strong>
                    <p>${post.content}</p>
                    <small>${new Date(post.created_at).toLocaleString()}</small>


                    <div id="comments-${post.id}" style="margin-top:10px"></div>

                    <input id="comment-${post.id}" 
                           placeholder="Write a comment..." 
                           style="width:70%">
                    <button onclick="submitComment(${post.id})">
                        Comment
                    </button>
                `;

                container.appendChild(div);

                loadComments(post.id);
            });
        })
        .catch(err => {
            console.error("Feed error:", err);
        });
}



/* ---------- LOAD APPROVED COMMENTS ---------- */
/* ---------- LOAD APPROVED COMMENTS WITH AI INFO ---------- */
function loadComments(postId) {
    fetch(`${API_BASE}/comments/approved/${postId}`)
        .then(res => res.json())
        .then(comments => {
            const container = document.getElementById(`comments-${postId}`);
            container.innerHTML = "";

            comments.forEach(c => {
                const p = document.createElement("p");
                p.innerHTML = `
                    <strong>${c.username}</strong>: ${c.text}
                    <br>
                    <small>Toxicity Score: ${c.toxicity_score}</small>
                `;
                container.appendChild(p);
            });
        });
}



// ---------- LOAD MY POSTS ----------
function loadMyPosts() {
    fetch(`${API_BASE}/my-posts/${currentUser.user_id}`)
        .then(res => res.json())
        .then(posts => {
            const container = document.getElementById("myPosts");
            container.innerHTML = "";

            if (posts.length === 0) {
                container.innerHTML = "<p>No posts yet</p>";
                return;
            }

            posts.forEach(post => {
                const div = document.createElement("div");
                div.style.border = "1px solid #ccc";
                div.style.padding = "10px";
                div.style.marginBottom = "10px";
                div.style.background = "#fff";
                div.style.color = "#000";

                div.innerHTML = `
                    <p>${post.content}</p>
                    <small>${post.created_at}</small>
                `;

                container.appendChild(div);
            });
        });
}


function loadPendingComments() {
    fetch(`${API_BASE}/my-posts/comments/${currentUser.user_id}`)
        .then(res => res.json())
        .then(comments => {
            const container = document.getElementById("moderationContainer");
            container.innerHTML = "";

            if (comments.length === 0) {
                container.innerHTML = "<p>No comments to review</p>";
                return;
            }

            comments.forEach(c => {
                const div = document.createElement("div");
                div.innerHTML = `
                    <p><strong>${c.commenter}</strong>: ${c.text}</p>
                    <small>Toxicity: ${c.toxicity_score}</small><br>
                    <button onclick="approveComment(${c.comment_id})">Approve</button>
                    <button onclick="rejectComment(${c.comment_id})">Reject</button>
                `;
                container.appendChild(div);
            });
        });
}
function loadNotifications() {
    fetch(`${API_BASE}/notifications/${currentUser.user_id}`)
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById("notificationContainer");
            container.innerHTML = "";

            if (data.length === 0) {
                container.innerHTML = "<p>No notifications</p>";
                return;
            }

            data.forEach(n => {
                const div = document.createElement("div");
                div.innerHTML = `
                    <p>${n.message}</p>
                    <small>${n.created_at}</small>
                `;
                container.appendChild(div);
            });
        });
}
function approveComment(commentId) {
    fetch(`${API_BASE}/comments/approve/${commentId}`, {
        method: "POST"
    }).then(() => {
        loadPendingComments();
    });
}

function rejectComment(commentId) {
    fetch(`${API_BASE}/comments/reject/${commentId}`, {
        method: "POST"
    }).then(() => {
        loadPendingComments();
    });
}
function createPost() {
    const content = document.getElementById("postContent").value;

    if (!content.trim()) {
        alert("Post cannot be empty");
        return;
    }

    fetch(`${API_BASE}/posts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: currentUser.user_id,
            content: content
        })
    })
    .then(res => res.json())
    .then(() => {
        document.getElementById("postContent").value = "";
        alert("Post created successfully");   // simple popup
        loadMyPosts();
        loadFeed();
    });
}
