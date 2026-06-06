;(function () {
    function getCookie(name) {
        const cookies = document.cookie ? document.cookie.split(';') : []
        for (const cookie of cookies) {
            const trimmed = cookie.trim()
            if (trimmed.startsWith(`${name}=`)) {
                return decodeURIComponent(trimmed.slice(name.length + 1))
            }
        }
        return ''
    }

    function escapeHtml(value) {
        return String(value == null ? '' : value)
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#39;')
    }

    function showAlert(alertEl, message, tone) {
        if (!alertEl) return
        alertEl.classList.remove('d-none', 'alert-success', 'alert-danger', 'alert-warning', 'alert-info')
        alertEl.classList.add(`alert-${tone || 'info'}`)
        alertEl.textContent = message
    }

    function hideAlert(alertEl) {
        if (!alertEl) return
        alertEl.classList.add('d-none')
    }

    async function parseJson(response) {
        try {
            return await response.json()
        } catch (err) {
            return {}
        }
    }

    function handleAuthError(status) {
        if (status === 401) {
            window.location.href = document.body.dataset.loginUrl || '/accounts/login/'
            return true
        }
        if (status === 403) {
            return true
        }
        return false
    }

    function initProfileCard() {
        const card = document.querySelector('[data-account-card]')
        if (!card) return

        const apiUrl = document.body.dataset.apiMeUrl
        const view = card.querySelector('[data-profile-view]')
        const form = card.querySelector('[data-profile-form]')
        const editButtons = card.querySelectorAll('[data-toggle-edit]')
        const errorBox = card.querySelector('[data-profile-error]')
        const successBox = card.querySelector('[data-profile-success]')

        if (!apiUrl || !form) return

        function setEditing(isEditing) {
            if (view) view.classList.toggle('d-none', isEditing)
            form.classList.toggle('d-none', !isEditing)
            editButtons.forEach(function (btn) {
                btn.hidden = isEditing
            })
        }

        editButtons.forEach(function (btn) {
            btn.addEventListener('click', function () {
                setEditing(form.classList.contains('d-none'))
            })
        })

        form.addEventListener('submit', async function (event) {
            event.preventDefault()
            hideAlert(errorBox)
            hideAlert(successBox)

            const formData = new FormData(form)
            const payload = {}
            formData.forEach(function (value, key) {
                payload[key] = String(value)
            })

            const submitBtn = form.querySelector('button[type="submit"]')
            const originalText = submitBtn ? submitBtn.textContent : ''
            if (submitBtn) {
                submitBtn.disabled = true
                submitBtn.textContent = 'Сохраняем...'
            }

            try {
                const response = await fetch(apiUrl, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify(payload),
                    credentials: 'same-origin',
                })

                if (handleAuthError(response.status)) {
                    return
                }

                const data = await parseJson(response)
                if (!response.ok) {
                    const message = data.detail || Object.values(data).join(' ')
                    throw new Error(message || 'Не удалось сохранить профиль.')
                }

                Object.keys(payload).forEach(function (key) {
                    const cell = view && view.querySelector(`[data-view="${key}"]`)
                    if (cell) {
                        cell.textContent = payload[key] || '—'
                    }
                })
                showAlert(successBox, 'Профиль обновлён', 'success')
                setEditing(false)
            } catch (err) {
                showAlert(errorBox, err.message || 'Ошибка сети.', 'danger')
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false
                    submitBtn.textContent = originalText
                }
            }
        })
    }

    document.addEventListener('DOMContentLoaded', function () {
        initProfileCard()
    })
})()
