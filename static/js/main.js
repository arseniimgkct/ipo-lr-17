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

    function isAuthError(status) {
        return status === 401 || status === 403
    }

    function redirectToLogin() {
        const loginUrl = document.body.dataset.loginUrl || '/accounts/login/'
        const next = encodeURIComponent(window.location.pathname + window.location.search)
        window.location.href = `${loginUrl}?next=${next}`
    }

    function escapeHtml(value) {
        return String(value)
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#39;')
    }

    function formatPrice(value) {
        return `${value} BYN`
    }

    function showNotification(message, tone) {
        const container = document.getElementById('notification-container')
        if (!container || !window.bootstrap) {
            return
        }

        const toneClass = tone || 'success'
        const wrapper = document.createElement('div')
        wrapper.className = 'toast align-items-center border-0'
        wrapper.setAttribute('role', 'alert')
        wrapper.setAttribute('aria-live', 'assertive')
        wrapper.setAttribute('aria-atomic', 'true')
        wrapper.innerHTML = `
      <div class="d-flex text-bg-${toneClass}">
        <div class="toast-body">${escapeHtml(message)}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Закрыть"></button>
      </div>
    `

        container.appendChild(wrapper)
        const toast = new window.bootstrap.Toast(wrapper, { delay: 3200 })
        wrapper.addEventListener('hidden.bs.toast', function () {
            wrapper.remove()
        })
        toast.show()
    }

    function updateCartCounter(count) {
        const counter = document.querySelector('[data-cart-counter]')
        if (!counter) {
            return
        }

        if (count > 0) {
            counter.textContent = count
            counter.classList.remove('d-none')
        } else {
            counter.textContent = '0'
            counter.classList.add('d-none')
        }
    }

    async function parseJson(response) {
        try {
            return await response.json()
        } catch {
            return {}
        }
    }

    async function addToCart(productId, count) {
        const url = document.body.dataset.cartApiAddUrl
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                product_id: productId,
                count: count,
            }),
        })

        const data = await parseJson(response)

        if (isAuthError(response.status)) {
            redirectToLogin()
            throw new Error(
                'Чтобы добавить товар в корзину, войдите в аккаунт.',
            )
        }

        if (!response.ok) {
            throw new Error(
                data.error ||
                    data.detail ||
                    'Не удалось добавить товар в корзину.',
            )
        }

        updateCartCounter(data.cart_items_count || 0)
        showNotification(data.message || 'Товар добавлен в корзину.', 'success')
        return data
    }

    function bindCartForms(root) {
        const scope = root || document
        const forms = scope.querySelectorAll('.js-cart-form')

        forms.forEach(function (form) {
            if (form.dataset.bound === 'true') {
                return
            }

            form.dataset.bound = 'true'

            form.addEventListener('submit', async function (event) {
                event.preventDefault()

                const productId = form.dataset.productId
                const button = form.querySelector('button[type="submit"]')
                const countInput = form.querySelector('[name="count"]')
                const count = countInput ? Number(countInput.value) || 1 : 1
                const originalText = button ? button.textContent : ''

                if (button) {
                    button.disabled = true
                    button.textContent = 'Добавляем...'
                }

                try {
                    await addToCart(productId, count)
                } catch (error) {
                    showNotification(error.message, 'danger')
                } finally {
                    if (button) {
                        button.disabled = false
                        button.textContent = originalText
                    }
                }
            })
        })
    }

    function buildCatalogCard(product) {
        const isAvailable = product.quantity_in_stock > 0
        const imageMarkup = product.image_url
            ? `<img src="${escapeHtml(product.image_url)}" class="card-img-top" alt="${escapeHtml(product.name)}">`
            : '<div class="product-placeholder">Bloom</div>'

        return `
      <div class="col-sm-6 col-lg-4">
        <article class="card product-card h-100 shadow-sm border-0">
          <div class="product-media">${imageMarkup}</div>
          <div class="card-body d-flex flex-column">
            <div class="product-meta">${escapeHtml(product.category.name)} • ${escapeHtml(product.producer.name)}</div>
            <h3 class="product-title"><a href="/catalog/${product.id}/">${escapeHtml(product.name)}</a></h3>
            <p class="product-description">${escapeHtml(product.description.slice(0, 95))}${product.description.length > 95 ? '...' : ''}</p>
            <div class="mt-auto">
              <div class="d-flex justify-content-between align-items-center mb-3 gap-3">
                <strong class="product-price">${formatPrice(product.price)}</strong>
                <span class="stock-pill ${isAvailable ? 'in-stock' : 'out-of-stock'}">
                  ${isAvailable ? 'В наличии' : 'Нет в наличии'}
                </span>
              </div>
              <div class="d-flex gap-2">
                <a class="btn btn-outline-bloom flex-grow-1" href="/catalog/${product.id}/">Подробнее</a>
                <button
                  class="btn btn-bloom"
                  type="button"
                  data-add-to-cart
                  data-product-id="${product.id}"
                  ${isAvailable ? '' : 'disabled'}
                >В корзину</button>
              </div>
            </div>
          </div>
        </article>
      </div>
    `
    }

    function renderCatalogPagination(
        container,
        totalCount,
        pageSize,
        currentPage,
        queryParams,
    ) {
        if (!container) {
            return
        }

        const totalPages = Math.ceil(totalCount / pageSize)
        if (totalPages <= 1) {
            container.innerHTML = ''
            return
        }

        const items = []

        function buildLink(page, label, isActive) {
            const params = new URLSearchParams(queryParams)
            params.set('page', String(page))
            const href = `${window.location.pathname}?${params.toString()}`
            return `
        <li class="page-item ${isActive ? 'active' : ''}">
          <a class="page-link" href="${href}" data-page-link="${page}">${label}</a>
        </li>
      `
        }

        if (currentPage > 1) {
            items.push(buildLink(currentPage - 1, 'Назад', false))
        }

        for (let page = 1; page <= totalPages; page += 1) {
            items.push(buildLink(page, String(page), page === currentPage))
        }

        if (currentPage < totalPages) {
            items.push(buildLink(currentPage + 1, 'Вперёд', false))
        }

        container.innerHTML = `<ul class="pagination justify-content-center flex-wrap">${items.join('')}</ul>`
    }

    function initCatalogPage() {
        const catalogPage = document.getElementById('catalog-page')
        if (!catalogPage) {
            return
        }

        const form = document.getElementById('catalog-filter-form')
        const grid = document.getElementById('catalog-products')
        const spinner = document.getElementById('catalog-spinner')
        const errorBox = document.getElementById('catalog-error')
        const pagination = document.getElementById('catalog-pagination')
        const resultsCount = document.getElementById('catalog-results-count')
        const pageSize = Number(catalogPage.dataset.pageSize || 9)

        async function loadCatalog(params, pushState) {
            const queryParams = new URLSearchParams(params)
            if (!queryParams.get('page')) {
                queryParams.set('page', '1')
            }

            if (pushState) {
                const nextUrl = `${window.location.pathname}?${queryParams.toString()}`
                window.history.pushState({}, '', nextUrl)
            }

            errorBox.classList.add('d-none')
            spinner.classList.remove('d-none')

            try {
                const response = await fetch(
                    `/api/products/?${queryParams.toString()}`,
                    {
                        headers: {
                            Accept: 'application/json',
                        },
                    },
                )
                const payload = await parseJson(response)

                if (!response.ok) {
                    throw new Error(
                        payload.detail || 'Не удалось загрузить товары из API.',
                    )
                }

                const products = Array.isArray(payload.results)
                    ? payload.results
                    : payload
                const totalCount = payload.count || products.length
                const currentPage = Number(queryParams.get('page') || 1)

                resultsCount.textContent = String(totalCount)

                if (!products.length) {
                    grid.innerHTML = `
            <div class="col-12">
              <div class="empty-state">
                <h3>По вашему запросу ничего не найдено</h3>
                <p class="mb-0">Попробуйте изменить категорию, производителя или текст поиска.</p>
              </div>
            </div>
          `
                } else {
                    grid.innerHTML = products.map(buildCatalogCard).join('')
                }

                renderCatalogPagination(
                    pagination,
                    totalCount,
                    pageSize,
                    currentPage,
                    queryParams,
                )
            } catch (error) {
                errorBox.textContent = error.message
                errorBox.classList.remove('d-none')
            } finally {
                spinner.classList.add('d-none')
            }
        }

        grid.addEventListener('click', async function (event) {
            const button = event.target.closest('[data-add-to-cart]')
            if (!button) {
                return
            }

            const originalText = button.textContent
            button.disabled = true
            button.textContent = 'Добавляем...'

            try {
                await addToCart(button.dataset.productId, 1)
            } catch (error) {
                showNotification(error.message, 'danger')
            } finally {
                button.disabled = false
                button.textContent = originalText
            }
        })

        pagination.addEventListener('click', function (event) {
            const link = event.target.closest('[data-page-link]')
            if (!link) {
                return
            }

            event.preventDefault()
            const params = new URLSearchParams(window.location.search)
            params.set('page', link.dataset.pageLink)
            loadCatalog(params, true)
            window.scrollTo({
                top: catalogPage.offsetTop - 80,
                behavior: 'smooth',
            })
        })

        form.addEventListener('submit', function (event) {
            event.preventDefault()

            const formData = new FormData(form)
            const params = new URLSearchParams()

            formData.forEach(function (value, key) {
                if (String(value).trim()) {
                    params.set(key, String(value).trim())
                }
            })

            params.set('page', '1')
            loadCatalog(params, true)
        })

        window.addEventListener('popstate', function () {
            const params = new URLSearchParams(window.location.search)
            const searchValue = params.get('search') || ''
            const categoryValue = params.get('category') || ''
            const producerValue = params.get('producer') || ''

            form.querySelector('[name="search"]').value = searchValue
            form.querySelector('[name="category"]').value = categoryValue
            form.querySelector('[name="producer"]').value = producerValue

            loadCatalog(params, false)
        })

        loadCatalog(new URLSearchParams(window.location.search), false)
    }

    document.addEventListener('DOMContentLoaded', function () {
        bindCartForms(document)
        initCatalogPage()
    })
})()
