document.addEventListener('DOMContentLoaded', () => {
    console.log('Customer Service Dashboard Initialized');
    document.body.classList.add('atendimento-view');

    // --- STATE ---
    let chats = [];
    let activeChatJid = null;
    let messages = [];
    let pollingInterval = null;
    let searchQuery = '';
    let selectedContactJids = new Set();
    let selectedFileNames = new Set();
    let lastFiles = [];
    const notificationSound = new Audio('https://assets.mixkit.co/active_storage/sfx/2358/2358-preview.mp3');
    const CHAT_WORKSPACE_STORAGE_KEY = 'fluxzap-chat-workspace';
    const QUICK_REPLY_LIBRARY_STORAGE_KEY = 'fluxzap-quick-replies';
    const CHAT_LIST_PREFERENCES_KEY = 'fluxzap-chat-list-preferences';
    const savedChatListPreferences = loadChatListPreferences();
    let currentFilter = savedChatListPreferences.currentFilter || 'all';
    let currentQueueFilter = savedChatListPreferences.currentQueueFilter || 'all';
    let currentStageFilter = savedChatListPreferences.currentStageFilter || 'all';
    let currentOperationalFocus = savedChatListPreferences.currentOperationalFocus || 'all';
    let operationalSummarySnapshots = {};
    let chatWorkspaceState = loadChatWorkspaceState();
    let quickReplyLibrary = loadQuickReplyLibrary();

    // Request Notification Permission
    if (Notification.permission !== "granted") {
        Notification.requestPermission();
    }

    // --- DOM ELEMENTS ---
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.content-section');
    const chatListContainer = document.getElementById('active-chats-list');
    const activeChatArea = document.getElementById('active-chat-area');
    const emptyChatState = document.getElementById('empty-chat-state');
    const messagesContainer = document.getElementById('messages-container');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const contactInfoPanel = document.getElementById('contact-info-panel');
    const chatSearchInput = document.getElementById('chat-search');
    const filterTabs = document.querySelectorAll('.chat-list-column .filter-tab[data-filter]');
    const operationalSummaryBar = document.getElementById('operational-summary-bar');
    const queueFilterBar = document.getElementById('queue-filter-bar');
    const stageFilterBar = document.getElementById('stage-filter-bar');
    const focusFilterBar = document.getElementById('focus-filter-bar');
    const filesSelectAll = document.getElementById('files-select-all');
    const filesDeleteSelectedBtn = document.getElementById('files-delete-selected');
    const filesSelectionStatus = document.getElementById('files-selection-status');
    const fileListContainer = document.getElementById('real-file-list');
    const uploadBtnTrigger = document.getElementById('upload-btn-trigger');
    const fileUploadInput = document.getElementById('file-upload-input');
    const toggleListFiltersBtn = document.getElementById('toggle-list-filters-btn');
    const chatListFilters = document.getElementById('chat-list-filters');
    const toggleComposerAssistBtn = document.getElementById('toggle-composer-assist-btn');
    const composerAssistPanel = document.getElementById('composer-assist-panel');

    // Header/Aside Info
    const headerChatName = document.getElementById('current-chat-name');
    const headerChatPill = document.getElementById('current-chat-pill');
    const headerChatMeta = document.getElementById('current-chat-meta');
    const headerChatStatus = document.getElementById('current-chat-status');
    const chatSlaValue = document.getElementById('chat-sla-value');
    const chatResponseValue = document.getElementById('chat-response-value');
    const chatMessageCount = document.getElementById('chat-message-count');
    const chatTagCount = document.getElementById('chat-tag-count');
    const chatStageCurrent = document.getElementById('chat-stage-current');
    const chatStageActions = document.getElementById('chat-stage-actions');
    const chatMicrostates = document.getElementById('chat-microstates');
    const chatRecentSummaryText = document.getElementById('chat-recent-summary-text');
    const chatLastAction = document.getElementById('chat-last-action');
    const chatNextStep = document.getElementById('chat-next-step');
    const composerPriorityPill = document.getElementById('composer-priority-pill');
    const composerContextLabel = document.getElementById('composer-context-label');
    const composerPlaybookGroups = document.getElementById('composer-playbook-groups');
    const composerQuickActions = document.getElementById('composer-quick-actions');
    const composerNotice = document.getElementById('composer-notice');
    const asideChatName = document.getElementById('aside-contact-name');
    const asideChatJid = document.getElementById('aside-contact-jid');
    const asideContactPill = document.getElementById('aside-contact-pill');
    const contactNotes = document.getElementById('contact-notes');
    const saveNotesBtn = document.getElementById('save-notes-btn');
    const contactTagsContainer = document.getElementById('contact-tags');
    const newTagInput = document.getElementById('new-tag-input');
    const addTagBtn = document.getElementById('add-tag-btn');

    // Header Actions
    const starBtn = document.querySelector('.header-actions .ri-star-line')?.parentElement || document.querySelector('.header-actions button:nth-child(1)');
    const archiveBtn = document.querySelector('.header-actions .ri-archive-line')?.parentElement || document.querySelector('.header-actions button:nth-child(2)');
    const blockBtn = document.getElementById('block-contact-btn');
    const chatAssumeBtn = document.getElementById('chat-assume-btn');
    const chatTransferBtn = document.getElementById('chat-transfer-btn');
    const chatCloseBtn = document.getElementById('chat-close-btn');

    // Settings Elements
    const apiURLInput = document.getElementById('setting-api-url');
    const apiTokenInput = document.getElementById('setting-api-token');
    const instanceNameInput = document.getElementById('setting-instance-name');
    const saveSettingsBtn = document.querySelector('#section-settings .btn-start');

    // Broadcast Elements
    const broadcastLeads = document.getElementById('broadcast-leads');
    const broadcastMessage = document.getElementById('broadcast-message');
    const broadcastTypeRadios = document.querySelectorAll('input[name="broadcast-type"]');
    const broadcastTextArea = document.getElementById('broadcast-text-area');
    const broadcastFileArea = document.getElementById('broadcast-file-area');
    const broadcastFileSelect = document.getElementById('broadcast-file-select');
    const broadcastFileCaption = document.getElementById('broadcast-file-caption');
    const broadcastFileSourceRadios = document.querySelectorAll('input[name="broadcast-file-source"]');
    const broadcastFileSourceManager = document.getElementById('broadcast-file-source-manager');
    const broadcastFileSourceLocal = document.getElementById('broadcast-file-source-local');
    const broadcastLocalFileInput = document.getElementById('broadcast-local-file');
    const broadcastLocalFileBtn = document.getElementById('broadcast-local-file-btn');
    const broadcastLocalFileName = document.getElementById('broadcast-local-file-name');
    const broadcastDelayMin = document.getElementById('broadcast-delay-min');
    const broadcastDelayMax = document.getElementById('broadcast-delay-max');
    const startBroadcastBtn = document.getElementById('start-broadcast-btn');
    const broadcastStatusPanel = document.getElementById('broadcast-status-panel');
    const broadcastGroupSelect = document.getElementById('broadcast-group-select');
    const broadcastGroupRefreshBtn = document.getElementById('broadcast-group-refresh');
    const broadcastGroupLoadBtn = document.getElementById('broadcast-group-load');
    const broadcastGroupSaveBtn = document.getElementById('broadcast-group-save');
    const broadcastGroupDeleteBtn = document.getElementById('broadcast-group-delete');
    const broadcastImportCsvInput = document.getElementById('broadcast-import-csv');
    const broadcastImportCsvBtn = document.getElementById('broadcast-import-csv-btn');
    const broadcastGroupInfo = document.getElementById('broadcast-group-info');

    // Modal Elements
    const imageModal = document.getElementById('image-modal');
    const modalImage = document.getElementById('modal-image');
    const modalClose = document.querySelector('.modal-close');

    // Instance Status Elements
    const instanceStatusBadge = document.getElementById('instance-status-badge');
    const instanceDisplayName = document.getElementById('instance-display-name');
    const detailsPhone = document.getElementById('details-phone');
    const detailsAvatar = document.getElementById('details-avatar');
    const detailsLastInteraction = document.getElementById('details-last-interaction');
    const detailsOrigin = document.getElementById('details-origin');
    const detailsOwner = document.getElementById('details-owner');

    // Contacts Elements
    const allContactsList = document.getElementById('all-contacts-list');
    const contactsSearchInput = document.getElementById('contacts-search');
    const contactsSyncBtn = document.getElementById('contacts-sync-btn');
    const contactsSyncStatus = document.getElementById('contacts-sync-status');
    const contactsGroupSelect = document.getElementById('contacts-group-select');
    const contactsGroupRefreshBtn = document.getElementById('contacts-group-refresh');
    const contactsGroupCreateBtn = document.getElementById('contacts-group-create');
    const contactsGroupAddSelectedBtn = document.getElementById('contacts-group-add-selected');
    const contactsGroupRenameBtn = document.getElementById('contacts-group-rename');
    const contactsGroupDeleteBtn = document.getElementById('contacts-group-delete');
    const contactsClearSelectionBtn = document.getElementById('contacts-clear-selection');
    const contactsSelectionStatus = document.getElementById('contacts-selection-status');
    const contactsGroupInfo = document.getElementById('contacts-group-info');
    const contactsGroupMembers = document.getElementById('contacts-group-members');

    // Dashboard Elements
    const dashInstanceAvatar = document.getElementById('dash-instance-avatar');
    const dashInstanceName = document.getElementById('dash-instance-name');
    const dashInstanceJid = document.getElementById('dash-instance-jid');
    const dashInstanceStatus = document.getElementById('dash-instance-status');
    const statContacts = document.getElementById('stat-contacts');
    const statChats = document.getElementById('stat-chats');
    const statMessages = document.getElementById('stat-messages');
    const dashRestartBtn = document.getElementById('dash-restart-btn');
    const dashLogoutBtn = document.getElementById('dash-logout-btn');

    // Agent (Flows) Elements
    const agentFlowSelect = document.getElementById('agent-flow-select');
    const agentFlowsRefreshBtn = document.getElementById('agent-flows-refresh');
    const agentFlowActivateBtn = document.getElementById('agent-flow-activate');
    const agentFlowCreateBtn = document.getElementById('agent-flow-create');
    const agentFlowRenameBtn = document.getElementById('agent-flow-rename');
    const agentFlowDeleteBtn = document.getElementById('agent-flow-delete');
    const agentBootstrapDefaultBtn = document.getElementById('agent-bootstrap-default');
    const agentRulesList = document.getElementById('agent-rules-list');
    const agentFlowStatus = document.getElementById('agent-flow-status');
    const agentRuleAddBtn = document.getElementById('agent-rule-add');

    // Theme Elements
    const themeLightBtn = document.getElementById('theme-light-btn');
    const themeDarkBtn = document.getElementById('theme-dark-btn');

    // --- THEME LOGIC ---
    function initTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        applyTheme(savedTheme);
    }

    function applyTheme(theme) {
        if (theme === 'dark') {
            document.body.classList.add('dark-theme');
            if (themeDarkBtn) themeDarkBtn.classList.add('active');
            if (themeLightBtn) themeLightBtn.classList.remove('active');
        } else {
            document.body.classList.remove('dark-theme');
            if (themeLightBtn) themeLightBtn.classList.add('active');
            if (themeDarkBtn) themeDarkBtn.classList.remove('active');
        }
        localStorage.setItem('theme', theme);
    }

    if (themeLightBtn) themeLightBtn.onclick = () => applyTheme('light');
    if (themeDarkBtn) themeDarkBtn.onclick = () => applyTheme('dark');

    initTheme();

    // --- COLLAPSIBLE DRAWERS LOGIC ---
    if (toggleListFiltersBtn && chatListFilters) {
        toggleListFiltersBtn.addEventListener('click', () => {
            chatListFilters.classList.toggle('collapsed');
            toggleListFiltersBtn.classList.toggle('is-active');
        });
    }

    if (toggleComposerAssistBtn && composerAssistPanel) {
        toggleComposerAssistBtn.addEventListener('click', () => {
            composerAssistPanel.classList.toggle('collapsed');
            toggleComposerAssistBtn.classList.toggle('is-active');
        });
    }

    // --- NAVIGATION ---
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetSectionId = item.getAttribute('data-section');
            if (!targetSectionId) return;

            navItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            sections.forEach(s => s.classList.remove('active'));
            const targetSection = document.getElementById(`section-${targetSectionId}`);
            if (targetSection) targetSection.classList.add('active');

            // Start/Stop Polling and class views based on section
            if (targetSectionId === 'atendimento') {
                document.body.classList.add('atendimento-view');
                startPolling();
            } else {
                document.body.classList.remove('atendimento-view');
                stopPolling();
            }

            if (targetSectionId === 'dashboard') {
                updateDashboard();
            }

            if (targetSectionId === 'contatos') {
                fetchContacts();
            }

            if (targetSectionId === 'files') {
                fetchFiles();
            }

            if (targetSectionId === 'mensagens') {
                fetchFilesForBroadcast();
                fetchContactGroups();
            }

            if (targetSectionId === 'agente') {
                fetchAgentFlows();
            }
        });
    });

    // --- SEARCH AND FILTERS ---
    chatSearchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value.toLowerCase();
        renderChatList();
    });

    filterTabs.forEach(tab => {
        tab.classList.toggle('active', tab.getAttribute('data-filter') === currentFilter);
        tab.addEventListener('click', () => {
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentFilter = tab.getAttribute('data-filter');
            persistChatListPreferences();
            renderChatList();
        });
    });

    function normalizeQueueKey(label) {
        return String(label || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/(^-|-$)/g, '');
    }

    function getTagQueueLabel(tagLabel) {
        const tag = String(tagLabel || '').toLowerCase();
        if (tag.includes('finance') || tag.includes('cobran')) return 'Financeiro';
        if (tag.includes('suporte') || tag.includes('erro') || tag.includes('bug')) return 'Suporte';
        if (tag.includes('venda') || tag.includes('comercial') || tag.includes('proposta')) return 'Comercial';
        if (tag.includes('agenda') || tag.includes('reuni') || tag.includes('visita')) return 'Agendamento';
        if (!tag) return '';
        return String(tagLabel).trim();
    }

    function getChatQueueLabel(chat) {
        const workspaceEntry = getWorkspaceEntry(chat?.jid);
        const tags = getChatTagsList(chat);

        if (workspaceEntry?.owner) return workspaceEntry.owner;
        if (tags.length > 0) return getTagQueueLabel(tags[0]);
        if (chat?.is_favorite) return 'Prioridade';
        return '';
    }

    function getDynamicQueueDefinitions() {
        const labels = [...new Set(
            chats
                .map(chat => getChatQueueLabel(chat))
                .filter(Boolean)
        )];

        return labels
            .sort((labelA, labelB) => labelA.localeCompare(labelB, 'pt-BR'))
            .slice(0, 5)
            .map(label => ({
                key: `queue:${normalizeQueueKey(label)}`,
                label
            }));
    }

    function getQueueFilterDefinitions() {
        return [
            { key: 'all', label: 'Todas as filas' },
            { key: 'assigned', label: 'Com você' },
            { key: 'pending', label: 'Pendentes' },
            { key: 'transferred', label: 'Transferidas' },
            { key: 'priority', label: 'Prioridade' },
            ...getDynamicQueueDefinitions()
        ];
    }

    function getStageFilterDefinitions() {
        const stageDefinitions = getStageDefinitions();
        const labelMap = Object.fromEntries(stageDefinitions.map(definition => [definition.key, definition.label]));
        labelMap.Acompanhamento = 'Acompanhar';
        labelMap.Atendimento = 'Atendimento';

        const knownStages = [...stageDefinitions.map(definition => definition.key), 'Atendimento'];
        const activeStages = [...new Set(chats.map(chat => getConversationStage(chat)).filter(Boolean))];
        const orderedStages = [
            ...knownStages.filter(stage => activeStages.includes(stage)),
            ...activeStages
                .filter(stage => !knownStages.includes(stage))
                .sort((stageA, stageB) => stageA.localeCompare(stageB, 'pt-BR'))
        ];

        return [
            { key: 'all', label: 'Todas as etapas' },
            ...orderedStages.map(stage => ({
                key: `stage:${normalizeQueueKey(stage)}`,
                label: labelMap[stage] || stage
            }))
        ];
    }

    function getOperationalFocusPresets() {
        return [
            {
                key: 'focus:diagnostico-critico',
                label: 'Diagnóstico crítico',
                tone: 'critical',
                matches: chat => getConversationStage(chat) === 'Diagnóstico' && getSlaConfig(chat).className === 'critical'
            },
            {
                key: 'focus:entrada-monitorada',
                label: 'Entrada monitorada',
                tone: 'warning',
                matches: chat => getConversationStage(chat) === 'Entrada' && Number(chat?.unread_count || 0) > 0
            },
            {
                key: 'focus:analise-prioritaria',
                label: 'Análise prioritária',
                tone: 'warning',
                matches: chat => getConversationStage(chat) === 'Análise' && Number(chat?.unread_count || 0) > 0
            },
            {
                key: 'focus:validacao-urgente',
                label: 'Validação urgente',
                tone: 'warning',
                matches: chat => getConversationStage(chat) === 'Validação' && ['critical', 'warning'].includes(getSlaConfig(chat).className)
            },
            {
                key: 'focus:transferencia-pendente',
                label: 'Transferência pendente',
                tone: 'info',
                matches: chat => getConversationStage(chat) === 'Transferência' && Number(chat?.unread_count || 0) > 0
            },
            {
                key: 'focus:retorno-atencao',
                label: 'Retorno em atenção',
                tone: 'warning',
                matches: chat => getConversationStage(chat) === 'Retorno' && ['critical', 'warning'].includes(getSlaConfig(chat).className)
            }
        ];
    }

    function getOperationalSummaryDefinitions() {
        return [
            {
                key: 'focus:critical',
                label: 'Críticos',
                tone: 'critical',
                matches: chat => getSlaConfig(chat).className === 'critical'
            },
            {
                key: 'focus:warning',
                label: 'Atenção',
                tone: 'warning',
                matches: chat => getSlaConfig(chat).className === 'warning'
            },
            {
                key: 'focus:transferencia-pendente',
                label: 'Transferências',
                tone: 'info',
                matches: chat => getConversationStage(chat) === 'Transferência' && Number(chat?.unread_count || 0) > 0
            }
        ];
    }

    function getOperationalFocusFilterDefinitions() {
        const summaryKeys = new Set(getOperationalSummaryDefinitions().map(definition => definition.key));
        return [
            ...getOperationalSummaryDefinitions(),
            ...getOperationalFocusPresets().filter(definition => !summaryKeys.has(definition.key))
        ];
    }

    function getOperationalFocusDefinitions() {
        const filterDefinitions = getOperationalFocusFilterDefinitions();
        const contextualChats = getChatsForOperationalSummary();
        const activeDefinitions = filterDefinitions
            .map(definition => ({
                ...definition,
                contextualCount: contextualChats.filter(chat => definition.matches(chat)).length
            }))
            .filter(definition => definition.contextualCount > 0)
            .sort((first, second) => {
                if (currentOperationalFocus === first.key) return -1;
                if (currentOperationalFocus === second.key) return 1;
                if (second.contextualCount !== first.contextualCount) return second.contextualCount - first.contextualCount;
                return first.label.localeCompare(second.label, 'pt-BR');
            });

        return [
            { key: 'all', label: 'Toda operação', tone: 'default' },
            ...activeDefinitions
        ];
    }

    function getOperationalFocusForChat(chat) {
        return getOperationalFocusPresets().find(definition => definition.matches(chat)) || null;
    }

    function getOperationalFocusDefinitionByKey(key) {
        return getOperationalFocusFilterDefinitions().find(definition => definition.key === key) || null;
    }

    function matchesQueueFilter(chat) {
        const workspaceEntry = getWorkspaceEntry(chat?.jid);
        if (currentQueueFilter === 'assigned') return workspaceEntry?.status === 'assigned';
        if (currentQueueFilter === 'pending') return Number(chat?.unread_count || 0) > 0;
        if (currentQueueFilter === 'transferred') return workspaceEntry?.status === 'transferred';
        if (currentQueueFilter === 'priority') return Boolean(chat?.is_favorite);
        if (currentQueueFilter.startsWith('queue:')) return currentQueueFilter === `queue:${normalizeQueueKey(getChatQueueLabel(chat))}`;
        return true;
    }

    function getQueueFilterCount(key) {
        return chats.filter(chat => {
            const workspaceEntry = getWorkspaceEntry(chat?.jid);
            if (key === 'assigned') return workspaceEntry?.status === 'assigned';
            if (key === 'pending') return Number(chat?.unread_count || 0) > 0;
            if (key === 'transferred') return workspaceEntry?.status === 'transferred';
            if (key === 'priority') return Boolean(chat?.is_favorite);
            if (String(key).startsWith('queue:')) return key === `queue:${normalizeQueueKey(getChatQueueLabel(chat))}`;
            return true;
        }).length;
    }

    function matchesStageFilter(chat) {
        if (currentStageFilter === 'all') return true;
        if (!String(currentStageFilter).startsWith('stage:')) return true;
        return currentStageFilter === `stage:${normalizeQueueKey(getConversationStage(chat))}`;
    }

    function getStageFilterCount(key) {
        return chats.filter(chat => {
            if (key === 'all') return true;
            if (!String(key).startsWith('stage:')) return true;
            return key === `stage:${normalizeQueueKey(getConversationStage(chat))}`;
        }).length;
    }

    function matchesOperationalFocus(chat) {
        if (currentOperationalFocus === 'all') return true;
        const focusDefinition = getOperationalFocusDefinitionByKey(currentOperationalFocus);
        return focusDefinition ? focusDefinition.matches(chat) : true;
    }

    function getOperationalFocusCount(key) {
        const contextualChats = getChatsForOperationalSummary();
        if (key === 'all') return contextualChats.length;
        const focusDefinition = getOperationalFocusDefinitionByKey(key);
        return focusDefinition ? contextualChats.filter(chat => focusDefinition.matches(chat)).length : contextualChats.length;
    }

    function matchesPrimaryChatFilter(chat) {
        return currentFilter === 'unread'
            ? Number(chat?.unread_count || 0) > 0
            : currentFilter === 'favorites'
                ? Boolean(chat?.is_favorite)
                : true;
    }

    function matchesSearchFilter(chat) {
        return (chat?.push_name || '').toLowerCase().includes(searchQuery) || (chat?.jid || '').includes(searchQuery);
    }

    function getChatsForOperationalSummary() {
        return chats.filter(chat => matchesSearchFilter(chat) && matchesPrimaryChatFilter(chat) && matchesQueueFilter(chat) && matchesStageFilter(chat));
    }

    function getOperationalSummaryContextKey() {
        return JSON.stringify({
            searchQuery,
            currentFilter,
            currentQueueFilter,
            currentStageFilter
        });
    }

    function getOperationalSummaryAlertCard(cards) {
        const tonePriority = {
            critical: 3,
            warning: 2,
            info: 1
        };

        return cards
            .filter(card => card.delta > 0)
            .sort((first, second) => {
                const priorityDifference = (tonePriority[second.tone] || 0) - (tonePriority[first.tone] || 0);
                if (priorityDifference !== 0) return priorityDifference;
                if (second.delta !== first.delta) return second.delta - first.delta;
                if (second.value !== first.value) return second.value - first.value;
                return first.label.localeCompare(second.label, 'pt-BR');
            })[0] || null;
    }

    function renderOperationalSummary() {
        if (!operationalSummaryBar) return;

        const contextualChats = getChatsForOperationalSummary();
        const contextKey = getOperationalSummaryContextKey();
        const previousSnapshot = operationalSummarySnapshots[contextKey] || null;
        const cards = getOperationalSummaryDefinitions().map(definition => ({
            ...definition,
            value: contextualChats.filter(chat => definition.matches(chat)).length
        })).map(card => {
            const previousValue = previousSnapshot?.[card.key];
            const delta = typeof previousValue === 'number' ? card.value - previousValue : 0;
            const trend = typeof previousValue !== 'number'
                ? 'initial'
                : delta > 0
                    ? 'up'
                    : delta < 0
                        ? 'down'
                        : 'flat';
            const trendLabel = trend === 'initial'
                ? 'Base inicial'
                : trend === 'up'
                    ? `+${delta} desde a última atualização`
                    : trend === 'down'
                        ? `${delta} desde a última atualização`
                        : 'Sem mudança';
            const trendSignal = trend === 'up' ? '↑' : trend === 'down' ? '↓' : '•';

            return {
                ...card,
                delta,
                trend,
                trendLabel,
                trendSignal
            };
        });
        const alertCard = getOperationalSummaryAlertCard(cards);

        operationalSummaryBar.innerHTML = cards.map(card => `
            <button type="button" class="${`operational-summary-card ${card.tone} ${currentOperationalFocus === card.key ? 'active' : ''} ${alertCard?.key === card.key ? 'surging' : ''}`.trim()}" data-focus-key="${escapeHtml(card.key)}">
                <span class="operational-summary-label">${card.label}</span>
                <span class="operational-summary-value">${card.value}</span>
                ${alertCard?.key === card.key ? '<span class="operational-summary-alert">Maior alta</span>' : ''}
                <span class="${`operational-summary-trend ${card.trend}`.trim()}">${card.trendSignal} ${card.trendLabel}</span>
            </button>
        `).join('');

        operationalSummarySnapshots[contextKey] = Object.fromEntries(cards.map(card => [card.key, card.value]));

        operationalSummaryBar.querySelectorAll('.operational-summary-card[data-focus-key]').forEach(card => {
            card.addEventListener('click', () => {
                const targetFocus = card.getAttribute('data-focus-key') || 'all';
                currentOperationalFocus = currentOperationalFocus === targetFocus ? 'all' : targetFocus;
                persistChatListPreferences();
                renderChatList();
            });
        });
    }

    function renderQueueFilters() {
        if (!queueFilterBar) return;

        const queueDefinitions = getQueueFilterDefinitions();
        if (!queueDefinitions.some(filter => filter.key === currentQueueFilter)) {
            currentQueueFilter = 'all';
            persistChatListPreferences();
        }

        queueFilterBar.innerHTML = '';
        queueDefinitions.forEach(filter => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = `queue-filter-btn ${currentQueueFilter === filter.key ? 'active' : ''}`.trim();
            button.textContent = `${filter.label} · ${getQueueFilterCount(filter.key)}`;
            button.onclick = () => {
                currentQueueFilter = filter.key;
                persistChatListPreferences();
                renderQueueFilters();
                renderChatList();
            };
            queueFilterBar.appendChild(button);
        });
    }

    function renderStageFilters() {
        if (!stageFilterBar) return;

        const stageDefinitions = getStageFilterDefinitions();
        if (!stageDefinitions.some(filter => filter.key === currentStageFilter)) {
            currentStageFilter = 'all';
            persistChatListPreferences();
        }

        stageFilterBar.innerHTML = '';
        stageDefinitions.forEach(filter => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = `stage-filter-btn ${currentStageFilter === filter.key ? 'active' : ''}`.trim();
            button.textContent = `${filter.label} · ${getStageFilterCount(filter.key)}`;
            button.onclick = () => {
                currentStageFilter = filter.key;
                persistChatListPreferences();
                renderStageFilters();
                renderChatList();
            };
            stageFilterBar.appendChild(button);
        });
    }

    function renderOperationalFocusFilters() {
        if (!focusFilterBar) return;

        const focusDefinitions = getOperationalFocusDefinitions();
        if (!focusDefinitions.some(filter => filter.key === currentOperationalFocus)) {
            currentOperationalFocus = 'all';
            persistChatListPreferences();
        }

        focusFilterBar.innerHTML = '';
        focusDefinitions.forEach(filter => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = `focus-filter-btn ${filter.tone || 'default'} ${currentOperationalFocus === filter.key ? 'active' : ''}`.trim();
            button.textContent = `${filter.label} · ${getOperationalFocusCount(filter.key)}`;
            button.onclick = () => {
                currentOperationalFocus = filter.key;
                persistChatListPreferences();
                renderOperationalFocusFilters();
                renderChatList();
            };
            focusFilterBar.appendChild(button);
        });
    }

    // --- API CALLS ---
    async function fetchChats() {
        try {
            const response = await fetch('/api/chats');
            chats = await response.json();
            if (activeChatJid) {
                const activeChat = chats.find(chat => chat.jid === activeChatJid);
                if (activeChat) {
                    updateChatContext(activeChat);
                    syncQuickActionButtons(activeChat);
                }
            }
            renderChatList();
        } catch (err) {
            console.error('Error fetching chats:', err);
        }
    }

    async function fetchMessages(jid) {
        if (!jid) return;
        try {
            const response = await fetch(`/api/messages/${jid}`);
            const newMessages = await response.json();
            const normalized = Array.isArray(newMessages) ? newMessages.map(m => {
                if (m && typeof m.metadata === 'string' && m.metadata) {
                    try { m.metadata = JSON.parse(m.metadata); } catch (e) { m.metadata = {}; }
                } else if (m && (m.metadata == null)) {
                    m.metadata = {};
                }
                return m;
            }) : [];

            // Only re-render if message count changed or first load
            if (normalized.length > messages.length && messages.length > 0) {
                const lastMsg = normalized[normalized.length - 1];
                if (!lastMsg.from_me) {
                    showNotification(lastMsg.sender, lastMsg.content);
                }
            }

            if (normalized.length !== messages.length) {
                messages = normalized;
                renderMessages();
            }
            const activeChat = chats.find(chat => chat.jid === jid);
            if (activeChat) {
                syncConversationStage(activeChat, normalized);
                renderConversationInsights(activeChat, normalized);
            }
        } catch (err) {
            console.error('Error fetching messages:', err);
        }
    }

    async function sendMessage() {
        const text = messageInput.value.trim();
        if (!text || !activeChatJid) return;

        messageInput.value = '';
        messageInput.style.height = 'auto';

        try {
            const resp = await fetch('/api/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jid: activeChatJid, text: text })
            });
            if (!resp.ok) {
                const data = await resp.json().catch(() => ({}));
                alert(`Falha ao enviar mensagem. ${data && data.response ? JSON.stringify(data.response) : ''}`);
            }
            const activeChat = chats.find(chat => chat.jid === activeChatJid);
            if (activeChat) {
                rememberQuickReply(activeChat, text);
                recordWorkspaceAction(activeChat.jid, 'message', 'Mensagem enviada');
                syncConversationStage(activeChat, messages, { stage: Number(activeChat.unread_count || 0) > 0 ? 'Retorno' : 'Acompanhamento' });
                renderComposerContext(activeChat, messages);
            }
            fetchMessages(activeChatJid); // Refresh immediately
        } catch (err) {
            console.error('Error sending message:', err);
            alert('Falha ao enviar mensagem. Verifique a conexão com a Evolution API.');
        }
    }

    async function saveContactNotes() {
        if (!activeChatJid) return;
        const notes = contactNotes.value;
        try {
            await fetch('/api/contacts/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jid: activeChatJid, notes: notes })
            });
            alert('Notas salvas com sucesso!');
        } catch (err) {
            console.error('Error saving notes:', err);
        }
    }

    async function saveContactData(updates) {
        if (!activeChatJid) return;
        try {
            await fetch('/api/contacts/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jid: activeChatJid, ...updates })
            });
            // Update local state and re-fetch if needed
            fetchChats();
            return true;
        } catch (err) {
            console.error('Error updating contact:', err);
            return false;
        }
    }

    async function fetchFiles() {
        try {
            const response = await fetch('/api/files');
            const files = await response.json();
            renderFileList(files);
        } catch (err) {
            console.error('Error fetching files:', err);
        }
    }

    function updateFilesSelectionStatus() {
        if (filesSelectionStatus) {
            const n = selectedFileNames ? selectedFileNames.size : 0;
            filesSelectionStatus.textContent = n ? `${n} selecionado(s)` : '';
        }
        if (filesSelectAll) {
            const total = Array.isArray(lastFiles) ? lastFiles.length : 0;
            filesSelectAll.checked = total > 0 && selectedFileNames.size === total;
            filesSelectAll.indeterminate = selectedFileNames.size > 0 && selectedFileNames.size < total;
        }
    }

    async function deleteSelectedFiles() {
        const toDelete = Array.from(selectedFileNames || []);
        if (toDelete.length === 0) return alert('Selecione pelo menos um arquivo.');
        if (!confirm(`Deseja excluir ${toDelete.length} arquivo(s)?`)) return;
        if (filesDeleteSelectedBtn) filesDeleteSelectedBtn.disabled = true;
        try {
            for (const name of toDelete) {
                try {
                    await fetch(`/api/files/${encodeURIComponent(name)}`, { method: 'DELETE' });
                } catch (e) { }
            }
        } finally {
            selectedFileNames = new Set();
            updateFilesSelectionStatus();
            if (filesDeleteSelectedBtn) filesDeleteSelectedBtn.disabled = false;
            fetchFiles();
        }
    }

    async function deleteFile(filename) {
        if (!confirm(`Deseja excluir o arquivo ${filename}?`)) return;
        try {
            await fetch(`/api/files/${filename}`, { method: 'DELETE' });
            fetchFiles();
        } catch (err) {
            console.error('Error deleting file:', err);
        }
    }

    async function renameFile(oldName) {
        const newName = prompt('Novo nome do arquivo:', oldName);
        if (!newName) return;
        try {
            const resp = await fetch(`/api/files/${encodeURIComponent(oldName)}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ new_name: newName })
            });
            const data = await resp.json().catch(() => ({}));
            if (!resp.ok || data.status !== 'success') {
                alert('Erro ao renomear: ' + (data.error || 'Erro desconhecido'));
                return;
            }
            fetchFiles();
        } catch (err) {
            console.error('Error renaming file:', err);
        }
    }

    async function uploadFiles(files) {
        const formData = new FormData();
        files.forEach(f => formData.append('file', f));
        try {
            const resp = await fetch('/api/files/upload', {
                method: 'POST',
                body: formData
            });
            const data = await resp.json();
            if (data.status === 'success') {
                fetchFiles();
                if (data.filenames) return data.filenames;
                if (data.filename) return [data.filename];
                return [];
            } else {
                alert('Erro no upload: ' + (data.error || 'Erro desconhecido'));
                return null;
            }
        } catch (err) {
            console.error('Error uploading file:', err);
            return null;
        }
    }

    // --- SETTINGS LOGIC ---
    async function loadSettings() {
        // Try to fetch current backend config first
        try {
            const resp = await fetch('/api/config');
            if (resp.ok) {
                const config = await resp.json();
                if (config.url) apiURLInput.value = config.url;
                if (config.token) apiTokenInput.value = config.token;
                if (config.instance) instanceNameInput.value = config.instance;
                return; // Use backend config as priority
            }
        } catch (e) {
            console.log('Backend config fetch failed, falling back to local storage', e);
        }

        const savedURL = localStorage.getItem('evolution_api_url');
        const savedToken = localStorage.getItem('evolution_api_token');
        const savedInstance = localStorage.getItem('evolution_instance_name');

        if (savedURL) apiURLInput.value = savedURL;
        if (savedToken) apiTokenInput.value = savedToken;
        if (savedInstance) instanceNameInput.value = savedInstance;
    }

    // --- CONTACTS LOGIC ---
    async function fetchContacts() {
        try {
            const resp = await fetch('/api/contacts');
            const data = await resp.json();
            renderContactsList(data);
        } catch (e) {
            console.error('Error fetching contacts', e);
        }
    }

    function updateContactsSelectionStatus() {
        if (!contactsSelectionStatus) return;
        const n = selectedContactJids ? selectedContactJids.size : 0;
        contactsSelectionStatus.textContent = n ? `${n} selecionado(s)` : '';
    }

    async function syncContacts() {
        if (contactsSyncBtn) contactsSyncBtn.disabled = true;
        if (contactsSyncStatus) contactsSyncStatus.textContent = 'Sincronizando...';
        try {
            await fetch('/api/contacts/sync', { method: 'POST' }).catch(() => null);

            const startedAt = Date.now();
            while (Date.now() - startedAt < 120000) {
                const statusResp = await fetch('/api/contacts/sync');
                const status = await statusResp.json().catch(() => ({}));
                if (status && status.running) {
                    if (contactsSyncStatus) contactsSyncStatus.textContent = 'Sincronizando...';
                    await new Promise(r => setTimeout(r, 1000));
                    continue;
                }
                if (status && status.last_error) {
                    if (contactsSyncStatus) contactsSyncStatus.textContent = 'Falha ao sincronizar.';
                    return;
                }
                if (status && status.last) {
                    if (contactsSyncStatus) contactsSyncStatus.textContent = `OK: importados ${status.last.imported || 0}, ignorados ${status.last.skipped || 0}.`;
                    fetchContacts();
                    return;
                }
                await new Promise(r => setTimeout(r, 1000));
            }

            if (contactsSyncStatus) contactsSyncStatus.textContent = 'Sincronização em andamento (aguarde).';
        } catch (e) {
            console.error('Error syncing contacts', e);
            if (contactsSyncStatus) contactsSyncStatus.textContent = 'Erro ao sincronizar.';
        } finally {
            if (contactsSyncBtn) contactsSyncBtn.disabled = false;
        }
    }

    function renderContactsList(contactsArray) {
        if (!allContactsList) return;
        allContactsList.innerHTML = '';

        if (contactsArray.length === 0) {
            allContactsList.innerHTML = '<div class="loading-state">Nenhum contato encontrado no banco de dados.</div>';
            return;
        }

        contactsArray.forEach(contact => {
            const card = document.createElement('div');
            card.className = 'contact-card-premium';

            const name = contact.push_name || 'Desconhecido';
            const jid = contact.jid;
            const phone = jid.split('@')[0];
            const letter = name[0].toUpperCase();
            const checked = selectedContactJids.has(jid);

            card.innerHTML = `
                <div class="contact-card-primary">
                    <div class="contact-card-avatar">${letter}</div>
                    <div class="contact-card-info">
                        <div class="contact-card-name">${name}</div>
                        <div class="contact-card-phone">${phone}</div>
                    </div>
                </div>
                <div class="contact-card-actions">
                    <label style="display:flex; align-items:center; gap:8px; cursor:pointer; margin-right:8px;">
                        <input class="contact-select-checkbox" type="checkbox" ${checked ? 'checked' : ''}>
                        <span style="font-size:12px; color: var(--text-muted);">Selecionar</span>
                    </label>
                    <button class="btn-icon" title="Iniciar Conversa"><i class="ri-chat-1-line"></i></button>
                </div>
            `;

            const checkbox = card.querySelector('.contact-select-checkbox');
            if (checkbox) {
                checkbox.onchange = (e) => {
                    e.stopPropagation();
                    if (checkbox.checked) selectedContactJids.add(jid);
                    else selectedContactJids.delete(jid);
                    updateContactsSelectionStatus();
                };
            }

            const startChatBtn = card.querySelector('.btn-icon');
            if (startChatBtn) {
                startChatBtn.onclick = (e) => {
                    e.stopPropagation();
                    const navAtendimento = document.querySelector('[data-section="atendimento"]');
                    if (navAtendimento) navAtendimento.click();
                    selectChat({ ...contact, push_name: name });
                };
            }

            allContactsList.appendChild(card);
        });
        updateContactsSelectionStatus();
    }

    if (contactsSearchInput) {
        contactsSearchInput.oninput = async (e) => {
            const query = e.target.value.toLowerCase();
            const resp = await fetch('/api/contacts');
            const data = await resp.json();
            const filtered = data.filter(c =>
                (c.push_name && c.push_name.toLowerCase().includes(query)) ||
                c.jid.includes(query) ||
                (c.notes && c.notes.toLowerCase().includes(query)) ||
                (c.tags && c.tags.toLowerCase().includes(query))
            );
            renderContactsList(filtered);
        };
    }

    if (contactsSyncBtn) {
        contactsSyncBtn.onclick = syncContacts;
    }

    async function createGroupFromSelected() {
        const name = prompt('Nome do grupo:', '');
        if (!name) return;
        const jids = Array.from(selectedContactJids || []);
        if (jids.length === 0) return alert('Selecione pelo menos um contato.');
        try {
            const respCreate = await fetch('/api/contact-groups', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });
            const created = await respCreate.json().catch(() => ({}));
            if (!respCreate.ok || created.status !== 'success') {
                return alert('Falha ao criar grupo.');
            }
            const groupId = created.id;
            const respAdd = await fetch(`/api/contact-groups/${encodeURIComponent(groupId)}/members`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jids })
            });
            const added = await respAdd.json().catch(() => ({}));
            if (!respAdd.ok || added.status !== 'success') {
                await fetchContactGroups();
                if (contactsGroupSelect) contactsGroupSelect.value = String(groupId);
                return alert('Grupo criado, mas falhou ao adicionar contatos.');
            }
            await fetchContactGroups();
            if (contactsGroupSelect) contactsGroupSelect.value = String(groupId);
            await loadContactsGroupMembers();
            selectedContactJids = new Set();
            updateContactsSelectionStatus();
            renderContactsList(await (await fetch('/api/contacts')).json());
        } catch (e) {
            console.error('Error creating group from selected', e);
            alert('Erro ao criar grupo.');
        }
    }

    async function addSelectedToExistingGroup() {
        const groupId = contactsGroupSelect ? contactsGroupSelect.value : '';
        if (!groupId) return alert('Selecione um grupo.');
        const jids = Array.from(selectedContactJids || []);
        if (jids.length === 0) return alert('Selecione pelo menos um contato.');
        try {
            const respAdd = await fetch(`/api/contact-groups/${encodeURIComponent(groupId)}/members`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jids })
            });
            const added = await respAdd.json().catch(() => ({}));
            if (!respAdd.ok || added.status !== 'success') {
                return alert('Falha ao adicionar contatos.');
            }
            await loadContactsGroupMembers();
            selectedContactJids = new Set();
            updateContactsSelectionStatus();
            renderContactsList(await (await fetch('/api/contacts')).json());
        } catch (e) {
            console.error('Error adding selected to group', e);
            alert('Erro ao adicionar no grupo.');
        }
    }

    function clearContactsSelection() {
        selectedContactJids = new Set();
        updateContactsSelectionStatus();
        fetchContacts();
    }

    async function loadContactsGroupMembers() {
        if (!contactsGroupMembers) return;
        const groupId = contactsGroupSelect ? contactsGroupSelect.value : '';
        if (!groupId) {
            contactsGroupMembers.innerHTML = '';
            if (contactsGroupInfo) contactsGroupInfo.textContent = '';
            return;
        }
        try {
            contactsGroupMembers.innerHTML = '<div class="loading-state">Carregando membros...</div>';
            if (contactsGroupInfo) contactsGroupInfo.textContent = '';
            const resp = await fetch(`/api/contact-groups/${encodeURIComponent(groupId)}/members`);
            const members = await resp.json();
            if (!resp.ok || !Array.isArray(members)) {
                contactsGroupMembers.innerHTML = '<div class="loading-state">Falha ao carregar membros.</div>';
                return;
            }

            if (contactsGroupInfo) contactsGroupInfo.textContent = `${members.length} membro(s) no grupo.`;
            if (members.length === 0) {
                contactsGroupMembers.innerHTML = '<div class="loading-state">Grupo sem membros.</div>';
                return;
            }

            contactsGroupMembers.innerHTML = '';
            members.forEach(m => {
                const jid = m.jid;
                const name = m.push_name || jid;
                const row = document.createElement('div');
                row.className = 'playbook-card';
                row.innerHTML = `
                    <div class="playbook-info">
                      <span class="playbook-name">${name}</span>
                      <span style="font-size: 12px; color: var(--text-muted);">${jid}</span>
                    </div>
                    <div class="playbook-actions">
                      <button class="btn-icon remove-member-btn" title="Remover do grupo">
                        <i class="ri-user-unfollow-line"></i>
                      </button>
                    </div>
                `;
                row.querySelector('.remove-member-btn').onclick = async () => {
                    if (!confirm('Remover este contato do grupo?')) return;
                    try {
                        const del = await fetch(`/api/contact-groups/${encodeURIComponent(groupId)}/members`, {
                            method: 'DELETE',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ jid })
                        });
                        const data = await del.json().catch(() => ({}));
                        if (!del.ok || data.status !== 'success') {
                            alert('Falha ao remover.');
                            return;
                        }
                        await loadContactsGroupMembers();
                    } catch (e) {
                        alert('Erro ao remover.');
                    }
                };
                contactsGroupMembers.appendChild(row);
            });
        } catch (e) {
            console.error('Error loading group members (contacts)', e);
            contactsGroupMembers.innerHTML = '<div class="loading-state">Erro ao carregar membros.</div>';
        }
    }

    async function renameSelectedContactsGroup() {
        const groupId = contactsGroupSelect ? contactsGroupSelect.value : '';
        if (!groupId) return alert('Selecione um grupo.');
        const name = prompt('Novo nome do grupo:', '');
        if (!name) return;
        try {
            const resp = await fetch(`/api/contact-groups/${encodeURIComponent(groupId)}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });
            const data = await resp.json().catch(() => ({}));
            if (!resp.ok || data.status !== 'success') {
                return alert('Falha ao renomear grupo.');
            }
            await fetchContactGroups();
            if (contactsGroupSelect) contactsGroupSelect.value = String(groupId);
        } catch (e) {
            alert('Erro ao renomear grupo.');
        }
    }

    async function deleteSelectedContactsGroup() {
        const groupId = contactsGroupSelect ? contactsGroupSelect.value : '';
        if (!groupId) return alert('Selecione um grupo.');
        if (!confirm('Deseja excluir este grupo?')) return;
        try {
            const resp = await fetch(`/api/contact-groups/${encodeURIComponent(groupId)}`, { method: 'DELETE' });
            const data = await resp.json().catch(() => ({}));
            if (!resp.ok || data.status !== 'success') {
                return alert('Falha ao excluir grupo.');
            }
            await fetchContactGroups();
            if (contactsGroupSelect) contactsGroupSelect.value = '';
            await loadContactsGroupMembers();
        } catch (e) {
            alert('Erro ao excluir grupo.');
        }
    }

    // --- DASHBOARD LOGIC ---
    async function updateDashboard() {
        fetchDashboardMetrics();
        updateDashboardInstanceInfo();
    }

    async function fetchDashboardMetrics() {
        try {
            const resp = await fetch('/api/metrics');
            const data = await resp.json();
            if (statContacts) statContacts.textContent = data.contacts || '0';
            if (statChats) statChats.textContent = data.chats || '0';
            if (statMessages) statMessages.textContent = data.messages || '0';
        } catch (e) {
            console.error('Error fetching metrics', e);
        }
    }

    async function updateDashboardInstanceInfo() {
        try {
            const resp = await fetch('/api/instance/status');
            const data = await resp.json();
            const state = data.instance ? data.instance.state : 'disconnected';
            const name = data.instance_name || 'Desconhecida';
            const jid = data.instance ? data.instance.ownerJid : 'Não disponível';

            if (dashInstanceName) dashInstanceName.textContent = name;
            if (dashInstanceJid) dashInstanceJid.textContent = jid;
            if (dashInstanceAvatar) dashInstanceAvatar.textContent = name[0].toUpperCase();

            if (dashInstanceStatus) {
                const indicator = dashInstanceStatus.querySelector('.status-indicator');
                const text = dashInstanceStatus.querySelector('span');

                indicator.className = 'status-indicator ' + (state === 'open' ? 'online' : (state === 'connecting' ? 'away' : 'offline'));
                text.textContent = state === 'open' ? 'Conectado' : (state === 'connecting' ? 'Conectando...' : 'Desconectado');

                // Style the pill background/text color based on state
                dashInstanceStatus.style.background = state === 'open' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)';
                dashInstanceStatus.style.color = state === 'open' ? '#15803d' : '#b91c1c';
            }
        } catch (e) {
            console.error('Error updating dashboard info', e);
        }
    }

    async function handleInstanceAction(action) {
        const endpoint = action === 'restart' ? '/api/instance/restart' : '/api/instance/logout';
        const label = action === 'restart' ? 'reiniciar' : 'desconectar';

        if (!confirm(`Deseja realmente ${label} a instância?`)) return;

        try {
            const resp = await fetch(endpoint, { method: 'POST' });
            const data = await resp.json();
            alert(data.message || `Ação de ${label} enviada com sucesso.`);
            updateDashboard();
        } catch (e) {
            alert(`Erro ao tentar ${label} a instância.`);
        }
    }

    function saveSettings() {
        const url = apiURLInput.value.trim();
        const token = apiTokenInput.value.trim();
        const instance = instanceNameInput.value.trim();

        if (!url || !token || !instance) {
            return alert('Preencha todos os campos de configuração.');
        }

        localStorage.setItem('evolution_api_url', url);
        localStorage.setItem('evolution_api_token', token);
        localStorage.setItem('evolution_instance_name', instance);

        alert('Configurações salvas no navegador!');
    }

    // --- STATUS LOGIC ---
    async function fetchInstanceStatus() {
        try {
            const resp = await fetch('/api/instance/status');
            const data = await resp.json();
            const state = data.instance ? data.instance.state : 'disconnected';
            const name = data.instance_name || 'Desconhecida';

            instanceDisplayName.textContent = name;
            const indicator = instanceStatusBadge.querySelector('.status-indicator');
            indicator.className = 'status-indicator ' + (state === 'open' ? 'online' : (state === 'connecting' ? 'away' : 'offline'));
            instanceStatusBadge.title = `Estado: ${state}`;
        } catch (e) {
            console.error('Error fetching instance status', e);
        }
    }
    async function fetchFilesForBroadcast() {
        try {
            const resp = await fetch('/api/files');
            const files = await resp.json();
            broadcastFileSelect.innerHTML = [`<option value="">Selecione um arquivo...</option>`, ...files.map(f => `<option value="${f.name}">${f.name}</option>`)].join('');
        } catch (e) { console.error('Error loading files for broadcast', e); }
    }

    async function fetchContactGroups() {
        try {
            const resp = await fetch('/api/contact-groups');
            const groups = await resp.json();

            const targets = [
                { el: broadcastGroupSelect, emptyText: 'Selecione um grupo...' },
                { el: contactsGroupSelect, emptyText: 'Selecione um grupo...' }
            ].filter(t => t.el);

            targets.forEach(t => {
                const previous = t.el.value;
                const options = [`<option value="">${t.emptyText}</option>`];
                if (Array.isArray(groups)) {
                    groups.forEach(g => options.push(`<option value="${g.id}">${g.name}</option>`));
                }
                t.el.innerHTML = options.join('');
                if (previous) t.el.value = previous;
            });
            if (contactsGroupSelect && contactsGroupSelect.value) {
                loadContactsGroupMembers();
            }
        } catch (e) {
            console.error('Error loading contact groups', e);
            if (broadcastGroupSelect) broadcastGroupSelect.innerHTML = `<option value="">Falha ao carregar</option>`;
            if (contactsGroupSelect) contactsGroupSelect.innerHTML = `<option value="">Falha ao carregar</option>`;
        }
    }

    function escapeHtml(value) {
        return String(value ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    async function fetchAgentFlows() {
        if (!agentFlowSelect) return;
        try {
            agentFlowSelect.innerHTML = `<option value="">Carregando...</option>`;
            if (agentRulesList) agentRulesList.innerHTML = `<div class="loading-state">Carregando regras...</div>`;
            if (agentFlowStatus) agentFlowStatus.textContent = '';

            const resp = await fetch('/api/flows');
            const flows = await resp.json();
            if (!resp.ok || !Array.isArray(flows)) {
                agentFlowSelect.innerHTML = `<option value="">Falha ao carregar</option>`;
                if (agentRulesList) agentRulesList.innerHTML = `<div class="loading-state">Falha ao carregar regras.</div>`;
                return;
            }

            const active = flows.find(f => f && (f.is_active === true || f.is_active === 1));
            const options = [`<option value="">Selecione um fluxo...</option>`];
            flows.forEach(f => {
                const id = f.id;
                const name = f.name || `Fluxo ${id}`;
                const suffix = (f.is_active === true || f.is_active === 1) ? ' (Ativo)' : '';
                options.push(`<option value="${id}">${escapeHtml(name)}${suffix}</option>`);
            });

            const previous = agentFlowSelect.value;
            agentFlowSelect.innerHTML = options.join('');
            if (previous) {
                agentFlowSelect.value = previous;
            } else if (active && active.id) {
                agentFlowSelect.value = String(active.id);
            }

            await fetchAgentRules();
        } catch (e) {
            console.error('Error loading flows', e);
            agentFlowSelect.innerHTML = `<option value="">Falha ao carregar</option>`;
            if (agentRulesList) agentRulesList.innerHTML = `<div class="loading-state">Falha ao carregar regras.</div>`;
        }
    }

    async function fetchAgentRules() {
        if (!agentFlowSelect || !agentRulesList) return;
        const flowId = agentFlowSelect.value;
        if (!flowId) {
            agentRulesList.innerHTML = `<div class="loading-state">Selecione um fluxo.</div>`;
            if (agentFlowStatus) agentFlowStatus.textContent = '';
            return;
        }
        try {
            agentRulesList.innerHTML = `<div class="loading-state">Carregando regras...</div>`;
            const resp = await fetch(`/api/flows/${encodeURIComponent(flowId)}/rules`);
            const rules = await resp.json();
            if (!resp.ok || !Array.isArray(rules)) {
                agentRulesList.innerHTML = `<div class="loading-state">Falha ao carregar regras.</div>`;
                return;
            }
            renderAgentRules(rules);
        } catch (e) {
            console.error('Error loading flow rules', e);
            agentRulesList.innerHTML = `<div class="loading-state">Erro ao carregar regras.</div>`;
        }
    }

    function renderAgentRules(rules) {
        if (!agentRulesList) return;
        if (!Array.isArray(rules) || rules.length === 0) {
            agentRulesList.innerHTML = `<div class="loading-state">Nenhuma regra neste fluxo.</div>`;
            if (agentFlowStatus) agentFlowStatus.textContent = '';
            return;
        }

        const enabledCount = rules.filter(r => r && (r.enabled === true || r.enabled === 1)).length;
        if (agentFlowStatus) agentFlowStatus.textContent = `${rules.length} regra(s) • ${enabledCount} ativa(s)`;

        agentRulesList.innerHTML = '';
        rules.forEach(r => {
            const id = r.id;
            const priority = r.priority ?? 100;
            const matchType = r.match_type || '';
            const matchValue = r.match_value || '';
            const actionType = r.action_type || '';
            const actionValue = r.action_value || '';
            const enabled = (r.enabled === true || r.enabled === 1);

            const triggerLabel = matchType === 'default'
                ? 'Padrão (fallback)'
                : `${matchType.toUpperCase()}: ${matchValue}`;
            const actionLabel = actionType === 'offers'
                ? `OFERTAS${actionValue ? ` • ${String(actionValue).slice(0, 80)}` : ''}`
                : `TEXTO • ${String(actionValue).slice(0, 80)}`;

            const card = document.createElement('div');
            card.className = 'playbook-card';
            card.innerHTML = `
                <div class="playbook-info">
                    <span class="playbook-name">#${escapeHtml(id)} • Prioridade ${escapeHtml(priority)}</span>
                    <span style="font-size: 12px; color: var(--text-muted);">Gatilho: ${escapeHtml(triggerLabel)}</span>
                    <span style="font-size: 12px; color: var(--text-muted);">Ação: ${escapeHtml(actionLabel)}</span>
                </div>
                <div class="playbook-actions">
                    <button class="btn-icon toggle-rule-btn" title="${enabled ? 'Desativar' : 'Ativar'}">
                        <i class="${enabled ? 'ri-toggle-fill' : 'ri-toggle-line'}"></i>
                    </button>
                    <button class="btn-icon edit-rule-btn" title="Editar">
                        <i class="ri-edit-line"></i>
                    </button>
                    <button class="btn-icon delete-rule-btn" title="Excluir">
                        <i class="ri-delete-bin-line"></i>
                    </button>
                </div>
            `;

            card.querySelector('.toggle-rule-btn').onclick = async () => {
                try {
                    const resp = await fetch(`/api/flow-rules/${encodeURIComponent(id)}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ enabled: !enabled })
                    });
                    const data = await resp.json().catch(() => ({}));
                    if (!resp.ok || data.status !== 'success') return alert('Falha ao atualizar regra.');
                    await fetchAgentRules();
                } catch (e) {
                    alert('Erro ao atualizar regra.');
                }
            };

            card.querySelector('.edit-rule-btn').onclick = async () => {
                const newPriority = prompt('Prioridade (menor executa primeiro):', String(priority));
                if (newPriority === null) return;
                const newMatchType = prompt('Tipo de gatilho: exact | contains | default', String(matchType || 'exact'));
                if (newMatchType === null) return;
                const mt = String(newMatchType).trim();
                let mv = matchValue;
                if (mt !== 'default') {
                    const newMatchValue = prompt('Valor do gatilho:', String(matchValue || ''));
                    if (newMatchValue === null) return;
                    mv = newMatchValue;
                } else {
                    mv = null;
                }
                const newActionType = prompt('Ação: text | offers', String(actionType || 'text'));
                if (newActionType === null) return;
                const at = String(newActionType).trim();
                let av = actionValue;
                if (at === 'text') {
                    const newText = prompt('Texto da resposta:', String(actionValue || ''));
                    if (newText === null) return;
                    av = newText;
                } else if (at === 'offers') {
                    const newIntro = prompt('Texto antes de enviar as ofertas (opcional):', String(actionValue || ''));
                    if (newIntro === null) return;
                    av = newIntro;
                } else {
                    return alert('Ação inválida.');
                }

                try {
                    const resp = await fetch(`/api/flow-rules/${encodeURIComponent(id)}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            priority: parseInt(newPriority) || 100,
                            match_type: mt,
                            match_value: mv,
                            action_type: at,
                            action_value: av
                        })
                    });
                    const data = await resp.json().catch(() => ({}));
                    if (!resp.ok || data.status !== 'success') return alert('Falha ao editar regra.');
                    await fetchAgentRules();
                } catch (e) {
                    alert('Erro ao editar regra.');
                }
            };

            card.querySelector('.delete-rule-btn').onclick = async () => {
                if (!confirm('Excluir esta regra?')) return;
                try {
                    const resp = await fetch(`/api/flow-rules/${encodeURIComponent(id)}`, { method: 'DELETE' });
                    const data = await resp.json().catch(() => ({}));
                    if (!resp.ok || data.status !== 'success') return alert('Falha ao excluir regra.');
                    await fetchAgentRules();
                } catch (e) {
                    alert('Erro ao excluir regra.');
                }
            };

            agentRulesList.appendChild(card);
        });
    }

    async function agentBootstrapDefault() {
        try {
            const resp = await fetch('/api/flows/bootstrap-default', { method: 'POST' });
            const data = await resp.json().catch(() => ({}));
            if (!resp.ok || data.status !== 'success') return alert('Falha ao carregar fluxo atual.');
            await fetchAgentFlows();
            if (agentFlowSelect) agentFlowSelect.value = String(data.flow_id);
            await fetchAgentRules();
        } catch (e) {
            alert('Erro ao carregar fluxo atual.');
        }
    }

    async function agentCreateFlow() {
        const name = prompt('Nome do fluxo:', '');
        if (!name) return;
        try {
            const resp = await fetch('/api/flows', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });
            const data = await resp.json().catch(() => ({}));
            if (!resp.ok || data.status !== 'success') return alert('Falha ao criar fluxo.');
            await fetchAgentFlows();
            if (agentFlowSelect) agentFlowSelect.value = String(data.id);
            await fetchAgentRules();
        } catch (e) {
            alert('Erro ao criar fluxo.');
        }
    }

    async function agentRenameFlow() {
        if (!agentFlowSelect) return;
        const flowId = agentFlowSelect.value;
        if (!flowId) return alert('Selecione um fluxo.');
        const name = prompt('Novo nome do fluxo:', '');
        if (!name) return;
        try {
            const resp = await fetch(`/api/flows/${encodeURIComponent(flowId)}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });
            const data = await resp.json().catch(() => ({}));
            if (!resp.ok || data.status !== 'success') return alert('Falha ao renomear fluxo.');
            await fetchAgentFlows();
            if (agentFlowSelect) agentFlowSelect.value = String(flowId);
            await fetchAgentRules();
        } catch (e) {
            alert('Erro ao renomear fluxo.');
        }
    }

    async function agentDeleteFlow() {
        if (!agentFlowSelect) return;
        const flowId = agentFlowSelect.value;
        if (!flowId) return alert('Selecione um fluxo.');
        if (!confirm('Excluir este fluxo e todas as regras?')) return;
        try {
            const resp = await fetch(`/api/flows/${encodeURIComponent(flowId)}`, { method: 'DELETE' });
            const data = await resp.json().catch(() => ({}));
            if (!resp.ok || data.status !== 'success') return alert('Falha ao excluir fluxo.');
            await fetchAgentFlows();
        } catch (e) {
            alert('Erro ao excluir fluxo.');
        }
    }

    async function agentActivateFlow() {
        if (!agentFlowSelect) return;
        const flowId = agentFlowSelect.value;
        if (!flowId) return alert('Selecione um fluxo.');
        try {
            const resp = await fetch(`/api/flows/${encodeURIComponent(flowId)}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ is_active: true })
            });
            const data = await resp.json().catch(() => ({}));
            if (!resp.ok || data.status !== 'success') return alert('Falha ao ativar fluxo.');
            await fetchAgentFlows();
            if (agentFlowSelect) agentFlowSelect.value = String(flowId);
            await fetchAgentRules();
        } catch (e) {
            alert('Erro ao ativar fluxo.');
        }
    }

    async function agentAddRule() {
        if (!agentFlowSelect) return;
        const flowId = agentFlowSelect.value;
        if (!flowId) return alert('Selecione um fluxo.');

        const matchType = prompt('Tipo de gatilho: exact | contains | default', 'exact');
        if (matchType === null) return;
        const mt = String(matchType).trim();

        let matchValue = null;
        if (mt !== 'default') {
            matchValue = prompt('Valor do gatilho:', '');
            if (matchValue === null) return;
            if (!String(matchValue).trim()) return alert('Informe o valor do gatilho.');
        }

        const actionType = prompt('Ação: text | offers', 'text');
        if (actionType === null) return;
        const at = String(actionType).trim();

        let actionValue = null;
        if (at === 'text') {
            actionValue = prompt('Texto da resposta:', '');
            if (actionValue === null) return;
            if (!String(actionValue).trim()) return alert('Informe o texto.');
        } else if (at === 'offers') {
            actionValue = prompt('Texto antes de enviar as ofertas (opcional):', '');
            if (actionValue === null) return;
        } else {
            return alert('Ação inválida.');
        }

        const priorityRaw = prompt('Prioridade (menor executa primeiro):', '100');
        if (priorityRaw === null) return;
        const enabled = confirm('Regra ativa?');

        try {
            const resp = await fetch(`/api/flows/${encodeURIComponent(flowId)}/rules`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    priority: parseInt(priorityRaw) || 100,
                    match_type: mt,
                    match_value: matchValue,
                    action_type: at,
                    action_value: actionValue,
                    enabled
                })
            });
            const data = await resp.json().catch(() => ({}));
            if (!resp.ok || data.status !== 'success') return alert('Falha ao adicionar regra.');
            await fetchAgentRules();
        } catch (e) {
            alert('Erro ao adicionar regra.');
        }
    }

    async function loadSelectedGroupToLeads() {
        if (!broadcastGroupSelect || !broadcastLeads) return;
        const groupId = broadcastGroupSelect.value;
        if (!groupId) return alert('Selecione um grupo.');
        try {
            if (broadcastGroupInfo) broadcastGroupInfo.textContent = 'Carregando contatos do grupo...';
            const resp = await fetch(`/api/contact-groups/${encodeURIComponent(groupId)}/members`);
            const members = await resp.json();
            if (!Array.isArray(members)) {
                if (broadcastGroupInfo) broadcastGroupInfo.textContent = 'Falha ao carregar membros.';
                return;
            }
            const jids = members.map(m => m.jid).filter(Boolean);
            broadcastLeads.value = jids.join('\n');
            if (broadcastGroupInfo) broadcastGroupInfo.textContent = `Carregado: ${jids.length} contatos.`;
        } catch (e) {
            console.error('Error loading group members', e);
            if (broadcastGroupInfo) broadcastGroupInfo.textContent = 'Erro ao carregar membros.';
        }
    }

    async function saveLeadsAsGroup() {
        if (!broadcastLeads) return;
        const raw = broadcastLeads.value.split('\n').map(l => l.trim()).filter(Boolean);
        if (raw.length === 0) return alert('Preencha o campo de destinatários primeiro.');
        const name = prompt('Nome do grupo:', '');
        if (!name) return;
        try {
            if (broadcastGroupInfo) broadcastGroupInfo.textContent = 'Criando grupo...';
            const respCreate = await fetch('/api/contact-groups', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });
            const created = await respCreate.json().catch(() => ({}));
            if (!respCreate.ok || created.status !== 'success') {
                if (broadcastGroupInfo) broadcastGroupInfo.textContent = 'Falha ao criar grupo.';
                return;
            }
            const groupId = created.id;
            const respAdd = await fetch(`/api/contact-groups/${encodeURIComponent(groupId)}/members`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jids: raw })
            });
            const added = await respAdd.json().catch(() => ({}));
            if (!respAdd.ok || added.status !== 'success') {
                if (broadcastGroupInfo) broadcastGroupInfo.textContent = 'Grupo criado, mas falhou ao adicionar membros.';
                await fetchContactGroups();
                return;
            }
            await fetchContactGroups();
            if (broadcastGroupSelect) broadcastGroupSelect.value = String(groupId);
            if (broadcastGroupInfo) broadcastGroupInfo.textContent = `Grupo criado: adicionados ${added.added || 0}.`;
        } catch (e) {
            console.error('Error saving group', e);
            if (broadcastGroupInfo) broadcastGroupInfo.textContent = 'Erro ao salvar grupo.';
        }
    }

    async function deleteSelectedGroup() {
        if (!broadcastGroupSelect) return;
        const groupId = broadcastGroupSelect.value;
        if (!groupId) return alert('Selecione um grupo.');
        if (!confirm('Deseja excluir este grupo?')) return;
        try {
            if (broadcastGroupInfo) broadcastGroupInfo.textContent = 'Excluindo...';
            const resp = await fetch(`/api/contact-groups/${encodeURIComponent(groupId)}`, { method: 'DELETE' });
            const data = await resp.json().catch(() => ({}));
            if (!resp.ok || data.status !== 'success') {
                if (broadcastGroupInfo) broadcastGroupInfo.textContent = 'Falha ao excluir.';
                return;
            }
            await fetchContactGroups();
            if (broadcastGroupInfo) broadcastGroupInfo.textContent = 'Grupo excluído.';
        } catch (e) {
            console.error('Error deleting group', e);
            if (broadcastGroupInfo) broadcastGroupInfo.textContent = 'Erro ao excluir.';
        }
    }

    async function importCsvToGroup(file) {
        if (!file) return;
        let groupId = broadcastGroupSelect ? broadcastGroupSelect.value : '';
        let groupName = '';
        if (!groupId) {
            groupName = prompt('Nome do grupo para importação:', '');
            if (!groupName) return;
        }
        try {
            if (broadcastGroupInfo) broadcastGroupInfo.textContent = 'Importando CSV...';
            const fd = new FormData();
            fd.append('file', file);
            if (groupId) fd.append('group_id', groupId);
            if (groupName) fd.append('group_name', groupName);
            const resp = await fetch('/api/contact-groups/import-csv', { method: 'POST', body: fd });
            const data = await resp.json().catch(() => ({}));
            if (!resp.ok || data.status !== 'success') {
                if (broadcastGroupInfo) broadcastGroupInfo.textContent = 'Falha na importação.';
                return;
            }
            await fetchContactGroups();
            if (broadcastGroupSelect) broadcastGroupSelect.value = String(data.group_id);
            if (broadcastGroupInfo) {
                broadcastGroupInfo.textContent = `Importado ${data.imported || 0}, adicionados ${data.added_to_group || 0}, ignorados ${data.skipped || 0}.`;
            }
        } catch (e) {
            console.error('Error importing CSV', e);
            if (broadcastGroupInfo) broadcastGroupInfo.textContent = 'Erro ao importar.';
        }
    }

    async function startBroadcast() {
        let leads = broadcastLeads.value.split('\n').map(l => l.trim()).filter(l => l);
        const selectedGroupId = broadcastGroupSelect ? broadcastGroupSelect.value : '';
        const type = document.querySelector('input[name="broadcast-type"]:checked').value;
        const message = broadcastMessage.value.trim();
        let fileName = broadcastFileSelect.value;
        const fileSource = document.querySelector('input[name="broadcast-file-source"]:checked')?.value || 'manager';
        const caption = (broadcastFileCaption && broadcastFileCaption.value ? broadcastFileCaption.value.trim() : '');
        const minDelay = parseInt(broadcastDelayMin.value) || 5;
        const maxDelay = parseInt(broadcastDelayMax.value) || 15;

        if (leads.length === 0 && selectedGroupId) {
            try {
                if (broadcastGroupInfo) broadcastGroupInfo.textContent = 'Carregando contatos do grupo...';
                const resp = await fetch(`/api/contact-groups/${encodeURIComponent(selectedGroupId)}/members`);
                const members = await resp.json();
                if (Array.isArray(members)) {
                    leads = members.map(m => m.jid).filter(Boolean);
                    if (broadcastGroupInfo) broadcastGroupInfo.textContent = `Grupo carregado: ${leads.length} contatos.`;
                } else {
                    if (broadcastGroupInfo) broadcastGroupInfo.textContent = 'Falha ao carregar contatos do grupo.';
                }
            } catch (e) {
                console.error('Error loading group for broadcast', e);
                if (broadcastGroupInfo) broadcastGroupInfo.textContent = 'Erro ao carregar contatos do grupo.';
            }
        }

        if (leads.length === 0) return alert('Insira pelo menos um destinatário.');
        if (type === 'text' && !message) return alert('Digite a mensagem.');
        if (type === 'file' && fileSource === 'manager' && !fileName) return alert('Selecione um arquivo.');
        if (type === 'file' && fileSource === 'local' && (!broadcastLocalFileInput || broadcastLocalFileInput.files.length === 0)) {
            return alert('Selecione um arquivo local.');
        }

        startBroadcastBtn.disabled = true;
        broadcastStatusPanel.innerHTML = `
          <div class="broadcast-progress-container">
              <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                  <span>Progresso: <strong id="bc-count">0</strong>/${leads.length}</span>
                  <span id="bc-percent">0%</span>
              </div>
              <div class="progress-bar-bg"><div id="bc-fill" class="progress-bar-fill"></div></div>
              <div id="bc-log" class="broadcast-log"></div>
          </div>
      `;

        const bcLog = document.getElementById('bc-log');
        const bcFill = document.getElementById('bc-fill');
        const bcCount = document.getElementById('bc-count');
        const bcPercent = document.getElementById('bc-percent');

        if (type === 'file' && fileSource === 'local') {
            const uploaded = await uploadFiles([broadcastLocalFileInput.files[0]]);
            if (!uploaded || uploaded.length === 0) {
                startBroadcastBtn.disabled = false;
                return alert('Falha ao enviar o arquivo para o servidor.');
            }
            fileName = uploaded[0];
        }

        for (let i = 0; i < leads.length; i++) {
            const rawLead = leads[i];
            let jid = rawLead;
            if (!rawLead.includes('@')) {
                const digits = rawLead.replace(/\D/g, '');
                if (!digits) {
                    const logEntry = document.createElement('div');
                    logEntry.className = 'log-entry error';
                    logEntry.textContent = `[${i + 1}] Erro: ${rawLead} (destinatário inválido: informe número ou JID)`;
                    bcLog.prepend(logEntry);
                    const pct = Math.round(((i + 1) / leads.length) * 100);
                    bcFill.style.width = pct + '%';
                    bcCount.textContent = i + 1;
                    bcPercent.textContent = pct + '%';
                    continue;
                }
                jid = `${digits}@s.whatsapp.net`;
            }
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry info';
            logEntry.textContent = `[${i + 1}] Enviando para ${rawLead}...`;
            bcLog.prepend(logEntry);

            try {
                let resp;
                if (type === 'text') {
                    resp = await fetch('/api/send', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ jid, text: message })
                    });
                } else {
                    resp = await fetch('/api/send/media', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ jid, filename: fileName, caption: caption || `Olá! Segue nossa oferta: ${fileName}` })
                    });
                }

                if (resp.ok) {
                    logEntry.className = 'log-entry success';
                    logEntry.textContent = `[${i + 1}] Sucesso: ${rawLead}`;
                } else {
                    const data = await resp.json().catch(() => ({}));
                    throw new Error(data && data.response ? JSON.stringify(data.response) : 'Erro API');
                }
            } catch (e) {
                logEntry.className = 'log-entry error';
                logEntry.textContent = `[${i + 1}] Erro: ${rawLead} (${e.message || 'falha'})`;
            }

            const pct = Math.round(((i + 1) / leads.length) * 100);
            bcFill.style.width = pct + '%';
            bcCount.textContent = i + 1;
            bcPercent.textContent = pct + '%';

            if (i < leads.length - 1) {
                const delay = Math.floor(Math.random() * (maxDelay - minDelay + 1) + minDelay) * 1000;
                await new Promise(r => setTimeout(r, delay));
            }
        }

        startBroadcastBtn.disabled = false;
        alert('Campanha finalizada!');
    }

    // --- UI HELPERS ---
    function openModal(src) {
        modalImage.src = src;
        imageModal.style.display = 'flex';
    }

    // --- RENDERING ---
    function renderChatList() {
        chatListContainer.innerHTML = '';
        renderOperationalSummary();
        renderQueueFilters();
        renderStageFilters();
        renderOperationalFocusFilters();

        let filteredChats = chats.filter(chat => {
            const matchesSearch = matchesSearchFilter(chat);
            if (!matchesSearch) return false;

            const matchesPrimaryFilter = matchesPrimaryChatFilter(chat);

            return matchesPrimaryFilter && matchesQueueFilter(chat) && matchesStageFilter(chat) && matchesOperationalFocus(chat);
        });

        if (filteredChats.length === 0) {
            chatListContainer.innerHTML = '<div class="loading-state">Nenhuma conversa encontrada.</div>';
            return;
        }

        filteredChats.sort(compareChatsByPriority);

        filteredChats.forEach(chat => {
            const item = document.createElement('div');
            const visualState = getChatVisualState(chat);
            const workspaceEntry = getWorkspaceEntry(chat.jid);
            const currentStage = getConversationStage(chat);
            const stageVisual = getStageVisualConfig(currentStage);
            const operationalFocus = getOperationalFocusForChat(chat);
            const focusToneClass = operationalFocus?.tone ? `focus-${operationalFocus.tone}` : '';
            const focusBadge = operationalFocus ? `<span class="chat-focus-badge ${operationalFocus.tone}">${escapeHtml(operationalFocus.label)}</span>` : '';
            item.className = `chat-item ${activeChatJid === chat.jid ? 'active' : ''} ${visualState.itemClasses} ${stageVisual.itemClass} ${focusToneClass}`.trim();
            const unreadBadge = chat.unread_count > 0 ? `<span class="unread-badge">${chat.unread_count}</span>` : '';
            const priorityDot = visualState.priorityClass ? `<span class="chat-priority-dot ${visualState.priorityClass}"></span>` : '';
            const waitTime = visualState.waitLabel ? `<span class="chat-wait-time">${escapeHtml(visualState.waitLabel)}</span>` : '';
            const ownerBadge = workspaceEntry?.owner ? `<span class="chat-owner-badge">${escapeHtml(workspaceEntry.owner)}</span>` : '';
            const actionBadge = getLastActionBadge(workspaceEntry) ? `<span class="chat-action-badge">${escapeHtml(getLastActionBadge(workspaceEntry))}</span>` : '';
            const stageBadge = `<span class="chat-stage-badge ${stageVisual.badgeClass}">${escapeHtml(currentStage)}</span>`;
            const chatName = escapeHtml(chat.push_name || 'Desconhecido');
            const chatPreview = escapeHtml(chat.last_msg || 'Sem mensagens');

            item.innerHTML = `
        <div class="avatar">${chat.push_name ? chat.push_name[0].toUpperCase() : '?'}</div>
        <div class="content">
          <div class="top">
            <span class="name">${chatName} ${unreadBadge}</span>
            <span class="time">${formatTime(chat.last_time)}</span>
          </div>
          <div class="preview">${chatPreview}</div>
          <div class="chat-meta">${priorityDot}${stageBadge}${focusBadge}${ownerBadge}${waitTime}</div>
          <div class="chat-meta chat-meta-secondary">${actionBadge}</div>
        </div>
      `;
            item.onclick = () => selectChat(chat);
            chatListContainer.appendChild(item);
        });
    }

    function renderMessages() {
        messagesContainer.innerHTML = '';
        const activeChat = chats.find(chat => chat.jid === activeChatJid);
        renderTimelineStatusBanner(activeChat);

        let currentDayLabel = '';
        messages.forEach(msg => {
            const messageDayLabel = formatMessageDay(msg.timestamp);
            if (messageDayLabel !== currentDayLabel) {
                currentDayLabel = messageDayLabel;
                const daySeparator = document.createElement('div');
                daySeparator.className = 'message-day-separator';
                const dayLabel = document.createElement('span');
                dayLabel.textContent = messageDayLabel;
                daySeparator.appendChild(dayLabel);
                messagesContainer.appendChild(daySeparator);
            }

            const div = document.createElement('div');
            div.className = `message ${msg.from_me ? 'sent' : 'received'} ${getMessageTypeClass(msg.type)}`.trim();

            const type = String(msg.type || 'text');
            const hasId = msg && msg.id != null && String(msg.id).trim() !== '';
            const messageLabel = document.createElement('div');
            messageLabel.className = 'message-label';
            messageLabel.textContent = msg.from_me ? 'Você' : (msg.sender || 'Cliente');

            const wrapper = document.createElement('div');
            wrapper.className = 'message-body';

            if (type === 'image') {
                const src = (msg.content && (String(msg.content).startsWith('http') || String(msg.content).startsWith('data:image') || String(msg.content).startsWith('/api/')))
                    ? String(msg.content)
                    : (hasId ? `/api/media/${encodeURIComponent(String(msg.id))}?raw=1` : '');

                if (src) {
                    const img = document.createElement('img');
                    img.src = src;
                    img.className = 'message-media message-image';
                    img.onclick = () => openModal(src);
                    wrapper.appendChild(img);
                } else {
                    wrapper.textContent = `🖼️ [Imagem] ${msg.content || ''}`;
                }
            } else if (type === 'audio') {
                if (hasId) {
                    const audio = document.createElement('audio');
                    audio.controls = true;
                    audio.src = `/api/media/${encodeURIComponent(String(msg.id))}?raw=1`;
                    audio.className = 'message-media message-audio';
                    wrapper.appendChild(audio);
                } else {
                    wrapper.textContent = '🎵 Áudio';
                }
            } else if (type === 'video') {
                if (hasId) {
                    const video = document.createElement('video');
                    video.controls = true;
                    video.src = `/api/media/${encodeURIComponent(String(msg.id))}?raw=1&mp4=1`;
                    video.className = 'message-media message-video';
                    wrapper.appendChild(video);
                } else {
                    wrapper.textContent = '🎥 Vídeo';
                }
            } else if (type === 'document') {
                const link = document.createElement('a');
                link.href = msg.content && String(msg.content).startsWith('/api/') ? String(msg.content) : '#';
                link.textContent = '📄 Abrir documento';
                link.target = '_blank';
                link.className = 'message-document-link';
                wrapper.appendChild(link);
            } else {
                wrapper.textContent = msg.content || '';
            }

            const meta = document.createElement('div');
            meta.className = 'message-meta';

            const typeBadge = document.createElement('span');
            typeBadge.className = 'message-type-badge';
            typeBadge.textContent = getMessageTypeLabel(type);

            const time = document.createElement('span');
            time.className = 'time';
            time.textContent = formatTime(msg.timestamp);

            meta.appendChild(typeBadge);
            meta.appendChild(time);

            div.appendChild(messageLabel);
            div.appendChild(wrapper);
            div.appendChild(meta);
            messagesContainer.appendChild(div);
        });
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function renderTags(chat) {
        contactTagsContainer.innerHTML = '';
        let tags = [];
        try {
            tags = typeof chat === 'string' ? JSON.parse(chat || '[]') : JSON.parse(chat.tags || '[]');
        } catch (e) { tags = []; }

        tags.forEach(tag => {
            const tagEl = document.createElement('span');
            tagEl.className = 'tag';
            const label = document.createElement('span');
            label.textContent = tag;
            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'tag-remove-btn';
            removeBtn.innerHTML = '<i class="ri-close-line"></i>';
            removeBtn.onclick = () => {
                const newTags = tags.filter(t => t !== tag);
                saveContactData({ tags: newTags });
                if (chat && typeof chat === 'object') chat.tags = JSON.stringify(newTags);
                renderTags(chat);
            };
            tagEl.appendChild(label);
            tagEl.appendChild(removeBtn);
            contactTagsContainer.appendChild(tagEl);
        });
    }

    function renderFileList(files) {
        fileListContainer.innerHTML = '';
        lastFiles = Array.isArray(files) ? files : [];
        const available = new Set(lastFiles.map(f => f && f.name).filter(Boolean));
        selectedFileNames = new Set(Array.from(selectedFileNames).filter(n => available.has(n)));
        updateFilesSelectionStatus();
        if (files.length === 0) {
            fileListContainer.innerHTML = '<div class="loading-state">Nenhum arquivo na pasta ofertas/</div>';
            return;
        }

        files.forEach(file => {
            const card = document.createElement('div');
            card.className = 'playbook-card';
            const checked = selectedFileNames.has(file.name);
            card.innerHTML = `
                <div class="playbook-info">
                  <span class="playbook-name">${file.name}</span>
                  <span style="font-size: 12px; color: var(--text-muted);">${file.type} • ${file.size}</span>
                </div>
                <div class="playbook-actions">
                  <label style="display:flex; align-items:center; gap:6px; cursor:pointer;">
                    <input class="file-select-checkbox" type="checkbox" ${checked ? 'checked' : ''}>
                  </label>
                  <button class="btn-icon rename-file-btn" title="Renomear">
                    <i class="ri-edit-line"></i>
                  </button>
                  <button class="btn-icon delete-file-btn" title="Excluir">
                    <i class="ri-delete-bin-line"></i>
                  </button>
                  <button class="btn-icon view-file-btn" title="Ver/Baixar">
                    <i class="ri-external-link-line"></i>
                  </button>
                </div>
            `;
            const checkbox = card.querySelector('.file-select-checkbox');
            if (checkbox) {
                checkbox.onchange = () => {
                    if (checkbox.checked) selectedFileNames.add(file.name);
                    else selectedFileNames.delete(file.name);
                    updateFilesSelectionStatus();
                };
            }
            card.querySelector('.delete-file-btn').onclick = () => deleteFile(file.name);
            card.querySelector('.rename-file-btn').onclick = () => renameFile(file.name);
            card.querySelector('.view-file-btn').onclick = () => window.open(`/api/files/${encodeURIComponent(file.name)}`, '_blank');
            fileListContainer.appendChild(card);
        });
        updateFilesSelectionStatus();
    }

    async function selectChat(chat) {
        activeChatJid = chat.jid;
        messages = []; // Clear current history

        // UI Updates
        emptyChatState.style.display = 'none';
        activeChatArea.style.display = 'flex';
        contactInfoPanel.style.display = 'block';

        headerChatName.textContent = chat.push_name || 'Contato';
        asideChatName.textContent = chat.push_name || 'Contato';
        asideChatJid.textContent = chat.jid;
        updateChatContext(chat);
        contactNotes.value = chat.notes || '';
        renderConversationInsights(chat, messages);

        // Load Avatar dynamically from API
        detailsAvatar.innerHTML = '<i class="ri-loader-4-line ri-spin"></i>';
        fetchContactAvatar(chat.jid);

        renderTags(chat);
        fetchMessages(chat.jid);
        fetchChats(); // Refresh list to update selection UI

        // Reset unread locally
        chat.unread_count = 0;
        updateChatContext(chat);

        renderChatList(); // Update active state class

        // Update Header Icon State
        if (starBtn && starBtn.querySelector('i')) {
            starBtn.querySelector('i').className = chat.is_favorite ? 'ri-star-fill' : 'ri-star-line';
            starBtn.querySelector('i').style.color = chat.is_favorite ? '#FFB800' : '';
        }
        syncQuickActionButtons(chat);
    }

    async function fetchContactAvatar(jid) {
        try {
            const resp = await fetch('/api/contacts/avatar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jid })
            });
            const data = await resp.json();
            if (data && data.profilePictureUrl) {
                detailsAvatar.innerHTML = `<img src="${data.profilePictureUrl}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;">`;
            } else {
                const name = headerChatName.textContent;
                detailsAvatar.innerHTML = name ? name[0].toUpperCase() : '?';
            }
        } catch (e) {
            detailsAvatar.innerHTML = '?';
        }
    }

    // --- HELPERS ---
    function displayId(jid) {
        if (!jid) return { phoneText: '' };
        if (jid.endsWith('@lid')) return { phoneText: 'ID (LID)' };
        return { phoneText: jid.split('@')[0] };
    }

    function escapeHtml(value) {
        return String(value ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function toDateValue(timestamp) {
        if (!timestamp) return null;
        const dateValue = typeof timestamp === 'number'
            ? new Date(timestamp < 1e12 ? timestamp * 1000 : timestamp)
            : new Date(timestamp);
        return Number.isNaN(dateValue.getTime()) ? null : dateValue;
    }

    function loadChatWorkspaceState() {
        try {
            return JSON.parse(localStorage.getItem(CHAT_WORKSPACE_STORAGE_KEY) || '{}');
        } catch (error) {
            return {};
        }
    }

    function persistChatWorkspaceState() {
        localStorage.setItem(CHAT_WORKSPACE_STORAGE_KEY, JSON.stringify(chatWorkspaceState));
    }

    function loadQuickReplyLibrary() {
        try {
            return JSON.parse(localStorage.getItem(QUICK_REPLY_LIBRARY_STORAGE_KEY) || '{}');
        } catch (error) {
            return {};
        }
    }

    function persistQuickReplyLibrary() {
        localStorage.setItem(QUICK_REPLY_LIBRARY_STORAGE_KEY, JSON.stringify(quickReplyLibrary));
    }

    function loadChatListPreferences() {
        try {
            const parsed = JSON.parse(localStorage.getItem(CHAT_LIST_PREFERENCES_KEY) || '{}');
            return {
                currentFilter: typeof parsed.currentFilter === 'string' ? parsed.currentFilter : 'all',
                currentQueueFilter: typeof parsed.currentQueueFilter === 'string' ? parsed.currentQueueFilter : 'all',
                currentStageFilter: typeof parsed.currentStageFilter === 'string' ? parsed.currentStageFilter : 'all',
                currentOperationalFocus: typeof parsed.currentOperationalFocus === 'string' ? parsed.currentOperationalFocus : 'all'
            };
        } catch (error) {
            return {
                currentFilter: 'all',
                currentQueueFilter: 'all',
                currentStageFilter: 'all',
                currentOperationalFocus: 'all'
            };
        }
    }

    function persistChatListPreferences() {
        localStorage.setItem(CHAT_LIST_PREFERENCES_KEY, JSON.stringify({
            currentFilter,
            currentQueueFilter,
            currentStageFilter,
            currentOperationalFocus
        }));
    }

    function getWorkspaceEntry(jid) {
        if (!jid) return null;
        return chatWorkspaceState[jid] || null;
    }

    function setWorkspaceEntry(jid, updates) {
        if (!jid) return;
        chatWorkspaceState[jid] = {
            ...(chatWorkspaceState[jid] || {}),
            ...updates,
            updatedAt: Date.now()
        };
        persistChatWorkspaceState();
    }

    function clearWorkspaceEntry(jid) {
        if (!jid || !chatWorkspaceState[jid]) return;
        delete chatWorkspaceState[jid];
        persistChatWorkspaceState();
    }

    function recordWorkspaceAction(jid, actionType, actionLabel) {
        if (!jid) return;
        setWorkspaceEntry(jid, {
            ...(getWorkspaceEntry(jid) || {}),
            lastActionType: actionType,
            lastActionLabel: actionLabel,
            lastActionAt: Date.now()
        });
    }

    function getLastActionBadge(entry) {
        if (!entry?.lastActionLabel) return '';
        const elapsedLabel = entry.lastActionAt ? formatCompactElapsed(entry.lastActionAt) : 'agora';
        return `${entry.lastActionLabel} · ${elapsedLabel}`;
    }

    function formatRelativeTime(timestamp) {
        const dateValue = toDateValue(timestamp);
        if (!dateValue) return 'Sem atividade recente';

        const diffMs = Date.now() - dateValue.getTime();
        const diffMinutes = Math.max(0, Math.floor(diffMs / 60000));

        if (diffMinutes < 1) return 'Agora mesmo';
        if (diffMinutes < 60) return `Há ${diffMinutes} min`;

        const diffHours = Math.floor(diffMinutes / 60);
        if (diffHours < 24) return `Há ${diffHours} h`;

        const diffDays = Math.floor(diffHours / 24);
        return `Há ${diffDays} d`;
    }

    function formatCompactElapsed(timestamp) {
        const dateValue = toDateValue(timestamp);
        if (!dateValue) return 'sem histórico';

        const diffMs = Date.now() - dateValue.getTime();
        const diffMinutes = Math.max(0, Math.floor(diffMs / 60000));

        if (diffMinutes < 60) return `${diffMinutes} min`;
        const diffHours = Math.floor(diffMinutes / 60);
        if (diffHours < 24) return `${diffHours} h`;
        const diffDays = Math.floor(diffHours / 24);
        return `${diffDays} d`;
    }

    function getRecentConversationSummary(currentMessages) {
        const safeMessages = Array.isArray(currentMessages) ? currentMessages : [];
        const recentMessages = safeMessages
            .slice(-3)
            .map(msg => {
                const author = msg.from_me ? 'Você' : (msg.sender || 'Cliente');
                const fallbackContent = getMessageTypeLabel(msg.type);
                const content = String(msg.content || fallbackContent).replace(/\s+/g, ' ').trim();
                return `${author}: ${content || fallbackContent}`;
            })
            .filter(Boolean);

        if (recentMessages.length === 0) return 'Sem histórico recente.';

        const summary = recentMessages.join(' • ');
        return summary.length > 220 ? `${summary.slice(0, 217)}...` : summary;
    }

    function formatMessageDay(timestamp) {
        const dateValue = toDateValue(timestamp);
        if (!dateValue) return 'Sem data';

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);

        const messageDay = new Date(dateValue);
        messageDay.setHours(0, 0, 0, 0);

        if (messageDay.getTime() === today.getTime()) return 'Hoje';
        if (messageDay.getTime() === yesterday.getTime()) return 'Ontem';

        return new Intl.DateTimeFormat('pt-BR', {
            day: '2-digit',
            month: 'long'
        }).format(dateValue);
    }

    function getMessageTypeLabel(type) {
        if (type === 'image') return 'Imagem';
        if (type === 'audio') return 'Áudio';
        if (type === 'video') return 'Vídeo';
        if (type === 'document') return 'Documento';
        return 'Texto';
    }

    function getMessageTypeClass(type) {
        return `message-type-${String(type || 'text')}`;
    }

    function getChatVisualState(chat) {
        const unreadCount = Number(chat.unread_count || 0);
        const lastMessageDate = toDateValue(chat.last_time);
        const minutesSinceLastMessage = lastMessageDate ? Math.max(0, Math.floor((Date.now() - lastMessageDate.getTime()) / 60000)) : 0;
        const isUrgent = unreadCount > 0 && minutesSinceLastMessage >= 30;
        const itemClasses = [unreadCount > 0 ? 'unread' : '', isUrgent ? 'urgent' : ''].filter(Boolean).join(' ');

        return {
            itemClasses,
            priorityClass: isUrgent ? 'urgent' : unreadCount > 0 ? 'unread' : '',
            waitLabel: unreadCount > 0
                ? `${formatRelativeTime(chat.last_time)} sem resposta`
                : `Última atividade ${formatRelativeTime(chat.last_time)}`
        };
    }

    function getChatPriorityScore(chat) {
        const workspaceEntry = getWorkspaceEntry(chat.jid);
        const unreadCount = Number(chat.unread_count || 0);
        const lastMessageDate = toDateValue(chat.last_time);
        const minutesSinceLastMessage = lastMessageDate ? Math.max(0, Math.floor((Date.now() - lastMessageDate.getTime()) / 60000)) : 0;
        const operationalFocus = getOperationalFocusForChat(chat);
        let score = 0;

        if (workspaceEntry?.status === 'assigned') score += 100;
        if (workspaceEntry?.status === 'transferred') score += 60;
        if (unreadCount > 0 && minutesSinceLastMessage >= 30) score += 80;
        if (unreadCount > 0) score += 40;
        if (chat.is_favorite) score += 20;
        if (operationalFocus?.tone === 'critical') score += 140;
        if (operationalFocus?.tone === 'warning') score += 90;
        if (operationalFocus?.tone === 'info') score += 60;

        return score;
    }

    function compareChatsByPriority(chatA, chatB) {
        const priorityDiff = getChatPriorityScore(chatB) - getChatPriorityScore(chatA);
        if (priorityDiff !== 0) return priorityDiff;

        const dateA = toDateValue(chatA.last_time)?.getTime() || 0;
        const dateB = toDateValue(chatB.last_time)?.getTime() || 0;
        return dateB - dateA;
    }

    function getChatStatusConfig(chat) {
        const workspaceEntry = getWorkspaceEntry(chat.jid);
        if (workspaceEntry?.status === 'assigned') {
            return {
                label: 'Com você',
                className: 'assigned',
                presence: 'atendimento assumido'
            };
        }

        if (workspaceEntry?.status === 'transferred') {
            return {
                label: 'Transferido',
                className: 'transferred',
                presence: `encaminhado para ${workspaceEntry.owner || 'outra fila'}`
            };
        }

        if (chat.is_favorite) {
            return {
                label: 'Favorita',
                className: 'favorite',
                presence: 'prioridade alta'
            };
        }

        if (Number(chat.unread_count || 0) > 0) {
            return {
                label: 'Nova',
                className: 'pending',
                presence: 'aguardando resposta'
            };
        }

        return {
            label: 'Em atendimento',
            className: '',
            presence: 'em acompanhamento'
        };
    }

    function getSlaConfig(chat) {
        const unreadCount = Number(chat?.unread_count || 0);
        const lastTime = chat?.last_time;
        const lastDate = toDateValue(lastTime);
        const minutesSinceLastInteraction = lastDate ? Math.max(0, Math.floor((Date.now() - lastDate.getTime()) / 60000)) : 0;

        if (unreadCount > 0 && minutesSinceLastInteraction >= 30) {
            return { label: 'Crítico', className: 'critical' };
        }

        if (unreadCount > 0 && minutesSinceLastInteraction >= 10) {
            return { label: 'Atenção', className: 'warning' };
        }

        if (unreadCount > 0) {
            return { label: 'Monitorando', className: 'monitoring' };
        }

        return { label: 'Em dia', className: 'healthy' };
    }

    function getConversationMetrics(chat, currentMessages) {
        const safeMessages = Array.isArray(currentMessages) ? currentMessages : [];
        const totalMessages = safeMessages.length;
        const totalTags = (() => {
            try {
                return JSON.parse(chat?.tags || '[]').length;
            } catch (error) {
                return 0;
            }
        })();
        const lastIncoming = [...safeMessages].reverse().find(msg => !msg.from_me);
        const lastOutgoing = [...safeMessages].reverse().find(msg => msg.from_me);
        const lastMessage = safeMessages[safeMessages.length - 1] || null;

        return {
            totalMessages,
            totalTags,
            lastIncoming,
            lastOutgoing,
            lastMessage
        };
    }

    function getStageDefinitions() {
        return [
            { key: 'Entrada', label: 'Entrada' },
            { key: 'Diagnóstico', label: 'Diagnóstico' },
            { key: 'Análise', label: 'Análise' },
            { key: 'Validação', label: 'Validação' },
            { key: 'Retorno', label: 'Retorno' },
            { key: 'Acompanhamento', label: 'Acompanhar' },
            { key: 'Transferência', label: 'Transferir' }
        ];
    }

    function getStageVisualConfig(stage) {
        if (stage === 'Entrada') return { badgeClass: 'stage-entrada', itemClass: 'stage-entrada' };
        if (stage === 'Diagnóstico') return { badgeClass: 'stage-diagnostico', itemClass: 'stage-diagnostico' };
        if (stage === 'Análise') return { badgeClass: 'stage-analise', itemClass: 'stage-analise' };
        if (stage === 'Validação') return { badgeClass: 'stage-validacao', itemClass: 'stage-validacao' };
        if (stage === 'Retorno') return { badgeClass: 'stage-retorno', itemClass: 'stage-retorno' };
        if (stage === 'Acompanhamento') return { badgeClass: 'stage-acompanhamento', itemClass: 'stage-acompanhamento' };
        if (stage === 'Transferência') return { badgeClass: 'stage-transferencia', itemClass: 'stage-transferencia' };
        return { badgeClass: '', itemClass: '' };
    }

    function getChatTagsList(chat) {
        try {
            const parsed = JSON.parse(chat?.tags || '[]');
            return Array.isArray(parsed) ? parsed.filter(Boolean) : [];
        } catch (error) {
            return [];
        }
    }

    function getChatContextCategory(chat) {
        const workspaceEntry = getWorkspaceEntry(chat?.jid);
        const tags = getChatTagsList(chat);

        if (workspaceEntry?.status === 'transferred') return 'transferência';
        if (workspaceEntry?.status === 'assigned') return 'assumido';
        if (tags.length > 0) return String(tags[0]).toLowerCase();
        if (Number(chat?.unread_count || 0) > 0) return 'pendência';
        if (chat?.is_favorite) return 'prioridade';
        return 'geral';
    }

    function getStoredQuickReplies(chat) {
        const category = getChatContextCategory(chat);
        return Array.isArray(quickReplyLibrary[category]) ? quickReplyLibrary[category] : [];
    }

    function inferConversationStage(chat, currentMessages = []) {
        const metrics = getConversationMetrics(chat, currentMessages);
        const workspaceEntry = getWorkspaceEntry(chat?.jid);
        const unreadCount = Number(chat?.unread_count || 0);
        const lastIncomingTime = toDateValue(metrics.lastIncoming?.timestamp)?.getTime() || 0;
        const lastOutgoingTime = toDateValue(metrics.lastOutgoing?.timestamp)?.getTime() || 0;
        const hasCustomerPending = unreadCount > 0 || lastIncomingTime > lastOutgoingTime;
        const latestIncomingType = String(metrics.lastIncoming?.type || '');
        const latestMessageType = String(metrics.lastMessage?.type || '');
        const evidenceType = hasCustomerPending ? latestIncomingType : latestMessageType;

        if (workspaceEntry?.status === 'transferred') return 'Transferência';
        if (hasCustomerPending && evidenceType === 'document') return 'Análise';
        if (hasCustomerPending && ['image', 'audio', 'video'].includes(evidenceType)) return 'Validação';
        if (metrics.lastIncoming && !metrics.lastOutgoing) return 'Entrada';
        if (hasCustomerPending) return 'Diagnóstico';
        if (latestMessageType === 'document') return 'Análise';
        if (['image', 'audio', 'video'].includes(latestMessageType)) return 'Validação';
        if (metrics.lastOutgoing) return chat?.is_favorite ? 'Acompanhamento' : 'Retorno';
        if (chat?.is_favorite) return 'Acompanhamento';
        return 'Atendimento';
    }

    function getConversationStage(chat, currentMessages = []) {
        const workspaceEntry = getWorkspaceEntry(chat?.jid);
        if (workspaceEntry?.status === 'transferred') return 'Transferência';
        if (workspaceEntry?.stageMode === 'manual' && workspaceEntry?.stage) return workspaceEntry.stage;
        if (workspaceEntry?.stage) return workspaceEntry.stage;
        return inferConversationStage(chat, currentMessages);
    }

    function getStagePlaybook(stage) {
        if (stage === 'Entrada') {
            return ['Saudar o cliente e confirmar a demanda.', 'Registrar o objetivo principal do atendimento.'];
        }
        if (stage === 'Diagnóstico') {
            return ['Coletar o detalhe que falta para seguir.', 'Validar a causa antes de orientar o cliente.'];
        }
        if (stage === 'Análise') {
            return ['Confirmar recebimento do material para análise.', 'Definir o retorno esperado após revisar o conteúdo.'];
        }
        if (stage === 'Validação') {
            return ['Revisar a evidência recebida e responder com encaminhamento.', 'Pedir um detalhe complementar somente se necessário.'];
        }
        if (stage === 'Retorno') {
            return ['Enviar atualização objetiva do andamento.', 'Confirmar se a orientação resolveu a solicitação.'];
        }
        if (stage === 'Transferência') {
            return ['Confirmar o novo responsável do atendimento.', 'Registrar repasse e alinhar expectativa de retorno.'];
        }
        if (stage === 'Acompanhamento') {
            return ['Manter o cliente atualizado sobre o andamento.', 'Registrar o próximo checkpoint interno.'];
        }
        return ['Confirmar entendimento da solicitação.', 'Validar próximo passo com o cliente.'];
    }

    function setConversationStage(chat, stage) {
        if (!chat?.jid || !stage) return;
        setWorkspaceEntry(chat.jid, {
            ...(getWorkspaceEntry(chat.jid) || {}),
            stage,
            stageMode: 'manual',
            stageUpdatedAt: Date.now()
        });
        recordWorkspaceAction(chat.jid, 'stage', `Etapa movida para ${stage}`);
        updateChatContext(chat);
        renderChatList();
    }

    function syncConversationStage(chat, currentMessages = [], options = {}) {
        if (!chat?.jid) return;
        const workspaceEntry = getWorkspaceEntry(chat.jid) || {};
        const nextStage = options.stage || inferConversationStage(chat, currentMessages);
        const shouldForce = Boolean(options.force);

        if (!nextStage) return;
        if (workspaceEntry.stageMode === 'manual' && !shouldForce) return;
        if (workspaceEntry.stage === nextStage && workspaceEntry.stageMode === 'auto' && !shouldForce) return;

        setWorkspaceEntry(chat.jid, {
            ...workspaceEntry,
            stage: nextStage,
            stageMode: 'auto',
            stageUpdatedAt: Date.now()
        });
    }

    function getTagPlaybookTemplates(tagLabel) {
        const tag = String(tagLabel || '').toLowerCase();

        if (tag.includes('finance') || tag.includes('cobran')) {
            return [
                { label: 'Financeiro', items: ['Vou validar a cobrança e já retorno.', 'Pode me confirmar o comprovante para seguir com a análise?'] }
            ];
        }

        if (tag.includes('suporte') || tag.includes('erro') || tag.includes('bug')) {
            return [
                { label: 'Suporte', items: ['Vou reproduzir o cenário para te orientar com precisão.', 'Pode me enviar a etapa em que isso acontece?'] }
            ];
        }

        if (tag.includes('venda') || tag.includes('comercial') || tag.includes('proposta')) {
            return [
                { label: 'Comercial', items: ['Vou preparar a melhor opção para você agora.', 'Posso te passar os próximos passos para fechamento.'] }
            ];
        }

        if (tag.includes('agenda') || tag.includes('reuni') || tag.includes('visita')) {
            return [
                { label: 'Agendamento', items: ['Posso confirmar a janela de horário desejada?', 'Vou alinhar a agenda e retorno com a confirmação.'] }
            ];
        }

        return [];
    }

    function rememberQuickReply(chat, text) {
        const normalized = String(text || '').replace(/\s+/g, ' ').trim();
        if (!chat || !normalized || normalized.length > 160) return;

        const category = getChatContextCategory(chat);
        const existing = getStoredQuickReplies(chat);
        quickReplyLibrary[category] = [normalized, ...existing.filter(item => item !== normalized)].slice(0, 6);
        persistQuickReplyLibrary();
    }

    function getOperationalSnapshot(chat, currentMessages) {
        const metrics = getConversationMetrics(chat, currentMessages);
        const workspaceEntry = getWorkspaceEntry(chat?.jid);
        const tags = getChatTagsList(chat);
        const primaryTag = tags[0] ? String(tags[0]) : '';
        const lastIncomingType = String(metrics.lastIncoming?.type || '');
        const lastMessageType = String(metrics.lastMessage?.type || '');
        const currentStage = getConversationStage(chat, currentMessages);

        let lastAction = 'Sem ação registrada.';
        if (workspaceEntry?.lastActionLabel) {
            lastAction = `${workspaceEntry.lastActionLabel} há ${formatCompactElapsed(workspaceEntry.lastActionAt)}.`;
        } else if (workspaceEntry?.status === 'transferred') {
            lastAction = `Transferência registrada para ${workspaceEntry.owner || 'outra fila'}.`;
        } else if (workspaceEntry?.status === 'assigned') {
            lastAction = `Conversa assumida por ${workspaceEntry.owner || 'você'}.`;
        } else if (lastMessageType === 'document') {
            lastAction = `Documento registrado há ${formatCompactElapsed(metrics.lastMessage.timestamp)}.`;
        } else if (lastMessageType === 'image') {
            lastAction = `Imagem recebida há ${formatCompactElapsed(metrics.lastMessage.timestamp)}.`;
        } else if (lastMessageType === 'audio') {
            lastAction = `Áudio recebido há ${formatCompactElapsed(metrics.lastMessage.timestamp)}.`;
        } else if (metrics.lastOutgoing) {
            lastAction = `Resposta enviada há ${formatCompactElapsed(metrics.lastOutgoing.timestamp)}.`;
        } else if (metrics.lastIncoming) {
            lastAction = `Cliente interagiu há ${formatCompactElapsed(metrics.lastIncoming.timestamp)}.`;
        }

        let nextStep = 'Acompanhar novos sinais da conversa.';
        if (currentStage === 'Entrada') {
            nextStep = 'Confirmar a demanda principal e alinhar o primeiro retorno.';
        } else if (currentStage === 'Diagnóstico') {
            nextStep = 'Consolidar informações faltantes antes de orientar o cliente.';
        } else if (currentStage === 'Análise') {
            nextStep = 'Revisar o material recebido e registrar o parecer.';
        } else if (currentStage === 'Validação') {
            nextStep = 'Validar a evidência com o cliente antes de concluir.';
        } else if (currentStage === 'Retorno') {
            nextStep = 'Enviar atualização objetiva e confirmar entendimento.';
        } else if (currentStage === 'Acompanhamento') {
            nextStep = 'Manter checkpoint ativo até a conclusão.';
        } else if (Number(chat?.unread_count || 0) > 0) {
            nextStep = 'Responder a pendência mais recente do cliente.';
        } else if (lastIncomingType === 'document' || lastMessageType === 'document') {
            nextStep = 'Validar o documento recebido e registrar retorno.';
        } else if (lastIncomingType === 'image' || lastMessageType === 'image') {
            nextStep = 'Conferir a imagem recebida antes de avançar.';
        } else if (lastIncomingType === 'audio' || lastMessageType === 'audio') {
            nextStep = 'Ouvir o áudio e sintetizar a orientação ao cliente.';
        } else if (lastIncomingType === 'video' || lastMessageType === 'video') {
            nextStep = 'Revisar o vídeo recebido e responder com o encaminhamento.';
        } else if (workspaceEntry?.status === 'transferred') {
            nextStep = 'Confirmar recebimento e alinhar o novo responsável.';
        } else if (chat?.is_favorite) {
            nextStep = 'Manter acompanhamento prioritário até o fechamento.';
        } else if (primaryTag) {
            nextStep = `Seguir o fluxo operacional da tag ${primaryTag}.`;
        }

        return { lastAction, nextStep };
    }

    function getPlaybookGroups(chat, currentMessages) {
        const metrics = getConversationMetrics(chat, currentMessages);
        const tags = getChatTagsList(chat);
        const stage = getConversationStage(chat, currentMessages);
        const groups = [
            {
                label: `Etapa · ${stage}`,
                items: getStagePlaybook(stage)
            }
        ];

        if (Number(chat?.unread_count || 0) > 0) {
            groups.push({
                label: 'Pendência',
                items: [
                    'Responder a mensagem mais recente.',
                    'Informar que o atendimento já está em andamento.'
                ]
            });
        }

        if (metrics.lastIncoming?.type === 'document' || metrics.lastMessage?.type === 'document') {
            groups.push({
                label: 'Documento',
                items: [
                    'Confirmar recebimento do documento.',
                    'Informar prazo de análise do arquivo.'
                ]
            });
        }

        if (metrics.lastIncoming?.type === 'image' || metrics.lastMessage?.type === 'image') {
            groups.push({
                label: 'Imagem',
                items: [
                    'Confirmar leitura da imagem enviada.',
                    'Solicitar um detalhe visual adicional, se necessário.'
                ]
            });
        }

        if (metrics.lastIncoming?.type === 'audio' || metrics.lastMessage?.type === 'audio') {
            groups.push({
                label: 'Áudio',
                items: [
                    'Avisar que o áudio será ouvido agora.',
                    'Responder com resumo objetivo do que foi entendido.'
                ]
            });
        }

        if (metrics.lastIncoming?.type === 'video' || metrics.lastMessage?.type === 'video') {
            groups.push({
                label: 'Vídeo',
                items: [
                    'Confirmar recebimento do vídeo antes de revisar.',
                    'Responder com o ponto principal validado no material.'
                ]
            });
        }

        tags.slice(0, 2).forEach(tag => {
            getTagPlaybookTemplates(tag).forEach(group => groups.push(group));
        });

        return groups
            .map(group => ({
                label: group.label,
                items: group.items.filter((item, index, self) => self.indexOf(item) === index).slice(0, 3)
            }))
            .filter(group => group.items.length > 0)
            .slice(0, 4);
    }

    function getQuickReplySuggestions(chat, currentMessages) {
        const suggestions = [...getStoredQuickReplies(chat)];
        const metrics = getConversationMetrics(chat, currentMessages);
        const workspaceEntry = getWorkspaceEntry(chat.jid);
        const lastIncoming = metrics.lastIncoming;

        if (Number(chat.unread_count || 0) > 0) {
            suggestions.push('Olá! Já estou verificando sua solicitação.');
        }

        if (workspaceEntry?.status === 'transferred') {
            suggestions.push('Recebi sua conversa e vou seguir por aqui.');
        }

        if (lastIncoming && String(lastIncoming.type || 'text') === 'document') {
            suggestions.push('Documento recebido. Vou analisar e retorno em seguida.');
        }

        if (lastIncoming && String(lastIncoming.type || 'text') === 'image') {
            suggestions.push('Imagem recebida. Vou conferir os detalhes agora.');
        }

        if (lastIncoming && String(lastIncoming.type || 'text') === 'audio') {
            suggestions.push('Áudio recebido. Vou ouvir e já te retorno com um resumo.');
        }

        if (lastIncoming && String(lastIncoming.type || 'text') === 'video') {
            suggestions.push('Vídeo recebido. Vou revisar o material e seguir com a orientação.');
        }

        if (chat.is_favorite) {
            suggestions.push('Estou priorizando seu atendimento neste momento.');
        }

        suggestions.push('Pode me confirmar mais um detalhe para eu continuar?');
        suggestions.push('Perfeito, vou avançar com isso agora.');

        return suggestions.filter((value, index, self) => self.indexOf(value) === index).slice(0, 6);
    }

    function updateStatusPill(element, statusConfig) {
        if (!element) return;
        element.textContent = statusConfig.label;
        element.classList.remove('pending', 'favorite', 'assigned', 'transferred');
        if (statusConfig.className) {
            element.classList.add(statusConfig.className);
        }
    }

    function updateChatContext(chat) {
        const display = displayId(chat.jid);
        const statusConfig = getChatStatusConfig(chat);
        const lastActivityLabel = formatRelativeTime(chat.last_time);
        const workspaceEntry = getWorkspaceEntry(chat.jid);

        if (headerChatStatus) headerChatStatus.textContent = statusConfig.presence;
        if (headerChatMeta) headerChatMeta.textContent = `Última mensagem ${lastActivityLabel}`;
        if (headerChatPill) updateStatusPill(headerChatPill, statusConfig);
        if (asideContactPill) updateStatusPill(asideContactPill, statusConfig);
        if (detailsPhone) detailsPhone.textContent = display.phoneText || '-';
        if (detailsLastInteraction) detailsLastInteraction.textContent = lastActivityLabel;
        if (detailsOrigin) detailsOrigin.textContent = workspaceEntry?.status === 'transferred' ? 'Transferência interna' : 'WhatsApp';
        if (detailsOwner) detailsOwner.textContent = workspaceEntry?.owner || (chat.is_favorite ? 'Atendimento prioritário' : 'Fila geral');
        renderConversationInsights(chat, messages);
    }

    function renderTimelineStatusBanner(chat) {
        if (!chat) return;

        const statusConfig = getChatStatusConfig(chat);
        const banner = document.createElement('div');
        banner.className = `timeline-status-banner ${statusConfig.className}`.trim();

        const badge = document.createElement('span');
        badge.className = 'timeline-status-pill';
        badge.textContent = statusConfig.label;

        const description = document.createElement('span');
        description.className = 'timeline-status-text';
        description.textContent = `${statusConfig.presence} • ${formatRelativeTime(chat.last_time)}`;

        banner.appendChild(badge);
        banner.appendChild(description);
        messagesContainer.appendChild(banner);
    }

    function renderConversationInsights(chat, currentMessages) {
        if (!chat) return;

        const metrics = getConversationMetrics(chat, currentMessages);
        const slaConfig = getSlaConfig(chat);
        const microstates = [];
        const workspaceEntry = getWorkspaceEntry(chat.jid);

        if (chatSlaValue) {
            chatSlaValue.textContent = slaConfig.label;
            chatSlaValue.className = `chat-insight-value ${slaConfig.className}`.trim();
        }

        if (chatResponseValue) {
            if (Number(chat.unread_count || 0) > 0) {
                chatResponseValue.textContent = `Cliente aguardando há ${formatCompactElapsed(chat.last_time)}`;
            } else if (metrics.lastOutgoing) {
                chatResponseValue.textContent = `Última resposta há ${formatCompactElapsed(metrics.lastOutgoing.timestamp)}`;
            } else {
                chatResponseValue.textContent = 'Sem resposta enviada';
            }
        }

        if (chatMessageCount) {
            chatMessageCount.textContent = metrics.totalMessages === 1 ? '1 mensagem' : `${metrics.totalMessages} mensagens`;
        }

        if (chatTagCount) {
            chatTagCount.textContent = `${metrics.totalTags} tag${metrics.totalTags === 1 ? '' : 's'}`;
        }

        const currentStage = getConversationStage(chat, currentMessages);
        if (chatStageCurrent) {
            chatStageCurrent.textContent = currentStage;
        }

        if (chatStageActions) {
            chatStageActions.innerHTML = '';
            getStageDefinitions().forEach(stageOption => {
                const button = document.createElement('button');
                button.type = 'button';
                button.className = `chat-stage-action ${currentStage === stageOption.key ? 'active' : ''}`.trim();
                button.textContent = stageOption.label;
                button.onclick = () => setConversationStage(chat, stageOption.key);
                chatStageActions.appendChild(button);
            });
        }

        if (chatMicrostates) {
            chatMicrostates.innerHTML = '';
        }


        renderComposerContext(chat, currentMessages);
    }

    function createComposerActionButton(chat, currentMessages, text, variant = 'default') {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = variant === 'playbook'
            ? 'composer-quick-action-btn composer-quick-action-btn-playbook'
            : 'composer-quick-action-btn';
        button.textContent = text;
        button.onclick = () => {
            rememberQuickReply(chat, text);
            recordWorkspaceAction(chat.jid, variant === 'playbook' ? 'playbook' : 'shortcut', variant === 'playbook' ? `Playbook aplicado` : 'Atalho reutilizado');
            const currentText = messageInput.value.trim();
            messageInput.value = currentText ? `${currentText}\n${text}` : text;
            messageInput.dispatchEvent(new Event('input'));
            messageInput.focus();
            renderComposerContext(chat, currentMessages);
        };
        return button;
    }

    function renderComposerContext(chat, currentMessages) {
        if (!chat) return;

        const metrics = getConversationMetrics(chat, currentMessages);
        const workspaceEntry = getWorkspaceEntry(chat.jid);
        const suggestions = getQuickReplySuggestions(chat, currentMessages);
        const playbookGroups = getPlaybookGroups(chat, currentMessages);
        const slaConfig = getSlaConfig(chat);
        const operationalSnapshot = getOperationalSnapshot(chat, currentMessages);
        const contextCategory = getChatContextCategory(chat);
        const currentStage = getConversationStage(chat, currentMessages);

        if (chatRecentSummaryText) {
            chatRecentSummaryText.textContent = getRecentConversationSummary(currentMessages);
        }

        if (chatLastAction) {
            chatLastAction.textContent = operationalSnapshot.lastAction;
        }

        if (chatNextStep) {
            chatNextStep.textContent = operationalSnapshot.nextStep;
        }

        if (composerPriorityPill) {
            composerPriorityPill.textContent = slaConfig.label;
            composerPriorityPill.className = `composer-priority-pill ${slaConfig.className}`.trim();
        }

        if (composerContextLabel) {
            composerContextLabel.textContent = `Contexto ${contextCategory} · Etapa ${currentStage}`;
        }

        if (sendBtn) {
            sendBtn.classList.remove('priority-critical', 'priority-warning', 'priority-monitoring');
            if (slaConfig.className === 'critical') sendBtn.classList.add('priority-critical');
            if (slaConfig.className === 'warning') sendBtn.classList.add('priority-warning');
            if (slaConfig.className === 'monitoring') sendBtn.classList.add('priority-monitoring');
        }

        if (composerNotice) {
            if (messageInput.value.trim()) {
                composerNotice.textContent = 'Rascunho em andamento. Enter envia, Shift+Enter quebra linha.';
            } else if (Number(chat.unread_count || 0) > 0) {
                composerNotice.textContent = `Pendência ativa: cliente aguardando há ${formatCompactElapsed(chat.last_time)}.`;
            } else if (workspaceEntry?.status === 'transferred') {
                composerNotice.textContent = `Conversa transferida para ${workspaceEntry.owner}.`;
            } else if (workspaceEntry?.stage) {
                composerNotice.textContent = `Etapa atual definida como ${workspaceEntry.stage}.`;
            } else if (metrics.lastOutgoing) {
                composerNotice.textContent = `Última resposta enviada há ${formatCompactElapsed(metrics.lastOutgoing.timestamp)}.`;
            } else {
                composerNotice.textContent = 'Sem pendências ativas no momento.';
            }
        }

        if (composerPlaybookGroups) {
            composerPlaybookGroups.innerHTML = '';
            playbookGroups.forEach(group => {
                const groupElement = document.createElement('div');
                groupElement.className = 'composer-playbook-group';

                const groupLabel = document.createElement('span');
                groupLabel.className = 'composer-section-label';
                groupLabel.textContent = group.label;

                const actions = document.createElement('div');
                actions.className = 'composer-playbook-actions';
                group.items.forEach(text => {
                    actions.appendChild(createComposerActionButton(chat, currentMessages, text, 'playbook'));
                });

                groupElement.appendChild(groupLabel);
                groupElement.appendChild(actions);
                composerPlaybookGroups.appendChild(groupElement);
            });
        }

        if (composerQuickActions) {
            composerQuickActions.innerHTML = '';
            suggestions.forEach(text => {
                composerQuickActions.appendChild(createComposerActionButton(chat, currentMessages, text));
            });
        }
    }

    function syncQuickActionButtons(chat) {
        const workspaceEntry = getWorkspaceEntry(chat?.jid);

        if (chatAssumeBtn) {
            const label = chatAssumeBtn.querySelector('span');
            if (label) label.textContent = workspaceEntry?.status === 'assigned' ? 'Assumido' : 'Assumir';
            chatAssumeBtn.classList.toggle('is-active', workspaceEntry?.status === 'assigned');
        }

        if (chatTransferBtn) {
            const label = chatTransferBtn.querySelector('span');
            if (label) label.textContent = workspaceEntry?.status === 'transferred' ? 'Transferido' : 'Transferir';
            chatTransferBtn.classList.toggle('is-active', workspaceEntry?.status === 'transferred');
        }
    }

    async function closeActiveChat() {
        if (!activeChatJid) return;
        if (!confirm('Deseja encerrar esta conversa?')) return;

        const updated = await saveContactData({ is_archived: 1 });
        if (!updated) {
            alert('Não foi possível encerrar a conversa agora.');
            return;
        }

        clearWorkspaceEntry(activeChatJid);
        activeChatJid = null;
        activeChatArea.style.display = 'none';
        emptyChatState.style.display = 'flex';
        contactInfoPanel.style.display = 'none';
        fetchChats();
    }

    function formatTime(timestamp) {
        if (!timestamp) return '';
        const d = (typeof timestamp === 'number')
            ? new Date(timestamp < 1e12 ? timestamp * 1000 : timestamp)
            : new Date(timestamp);
        if (isNaN(d.getTime())) return '';
        return new Intl.DateTimeFormat('pt-BR', { timeZone: 'America/Sao_Paulo', hour: '2-digit', minute: '2-digit' }).format(d);
    }

    function startPolling() {
        stopPolling();
        fetchChats();
        pollingInterval = setInterval(() => {
            fetchChats();
            if (activeChatJid) fetchMessages(activeChatJid);
        }, 3000);
    }

    function stopPolling() {
        if (pollingInterval) clearInterval(pollingInterval);
    }

    function showNotification(sender, text) {
        if (Notification.permission === "granted") {
            new Notification(`Mensagem de ${sender}`, {
                body: text,
                icon: 'https://cdn-icons-png.flaticon.com/512/124/124034.png'
            });
        }
        notificationSound.play().catch(e => console.log('Sound blocked by browser policy'));
    }

    // --- EVENT LISTENERS ---
    // Message Input
    if (messageInput) {
        let typingTimeout = null;
        messageInput.addEventListener('input', () => {
            if (!activeChatJid) return;

            // Send typing presence
            if (!typingTimeout) {
                fetch('/api/instance/presence', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ jid: activeChatJid, presence: 'composing' })
                });
            }

            clearTimeout(typingTimeout);
            typingTimeout = setTimeout(() => {
                typingTimeout = null;
                // Stop typing after 3 seconds of inactivity
                fetch('/api/instance/presence', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ jid: activeChatJid, presence: 'paused' })
                });
            }, 3000);
        });

        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    sendBtn.onclick = sendMessage; // Keep this for button click
    if (saveNotesBtn) {
        saveNotesBtn.onclick = () => saveContactData({ notes: contactNotes?.value });
    }

    // Toggle details open when clicking chat header info
    const contactInfoMini = document.querySelector('.contact-info-mini');
    const agentPanel = document.querySelector('.agent-panel');
    if (contactInfoMini && agentPanel) {
        contactInfoMini.style.cursor = 'pointer';
        contactInfoMini.addEventListener('click', () => {
            agentPanel.classList.toggle('details-open');
        });
    }

    // Action buttons inside details panel proxying header actions
    const asideAssumeBtn = document.getElementById('aside-assume-btn');
    const asideTransferBtn = document.getElementById('aside-transfer-btn');
    const asideCloseBtn = document.getElementById('aside-close-btn');
    if (asideAssumeBtn) asideAssumeBtn.onclick = () => chatAssumeBtn?.click();
    if (asideTransferBtn) asideTransferBtn.onclick = () => chatTransferBtn?.click();
    if (asideCloseBtn) asideCloseBtn.onclick = () => chatCloseBtn?.click();

    addTagBtn.onclick = () => {
        const tag = newTagInput.value.trim();
        if (!tag || !activeChatJid) return;
        const chat = chats.find(c => c.jid === activeChatJid);
        if (!chat) return;
        let tags = [];
        try { tags = JSON.parse(chat.tags || '[]'); } catch (e) { }
        if (!tags.includes(tag)) {
            tags.push(tag);
            saveContactData({ tags: tags });
            chat.tags = JSON.stringify(tags);
            renderTags(chat);
        }
        newTagInput.value = '';
    };

    if (starBtn) {
        starBtn.onclick = () => {
            if (!activeChatJid) return;
            const chat = chats.find(c => c.jid === activeChatJid);
            if (!chat) return;
            const newState = chat.is_favorite ? 0 : 1;
            chat.is_favorite = newState;
            saveContactData({ is_favorite: newState });
            recordWorkspaceAction(chat.jid, 'priority', newState ? 'Prioridade ativada' : 'Prioridade removida');
            if (starBtn.querySelector('i')) {
                starBtn.querySelector('i').className = newState ? 'ri-star-fill' : 'ri-star-line';
                starBtn.querySelector('i').style.color = newState ? '#FFB800' : '';
            }
            updateChatContext(chat);
            renderChatList();
        };
    }

    if (chatAssumeBtn) {
        chatAssumeBtn.onclick = () => {
            if (!activeChatJid) return;
            const chat = chats.find(c => c.jid === activeChatJid);
            if (!chat) return;

            setWorkspaceEntry(chat.jid, {
                status: 'assigned',
                owner: 'Você'
            });
            recordWorkspaceAction(chat.jid, 'assigned', 'Conversa assumida');
            syncConversationStage(chat, messages, { stage: Number(chat.unread_count || 0) > 0 ? 'Diagnóstico' : 'Acompanhamento' });
            updateChatContext(chat);
            syncQuickActionButtons(chat);
            renderChatList();
        };
    }

    if (chatTransferBtn) {
        chatTransferBtn.onclick = () => {
            if (!activeChatJid) return;
            const chat = chats.find(c => c.jid === activeChatJid);
            if (!chat) return;

            const destination = prompt('Transferir para qual responsável ou fila?', getWorkspaceEntry(chat.jid)?.owner || '');
            if (!destination || !destination.trim()) return;

            setWorkspaceEntry(chat.jid, {
                status: 'transferred',
                owner: destination.trim()
            });
            recordWorkspaceAction(chat.jid, 'transferred', `Transferida para ${destination.trim()}`);
            syncConversationStage(chat, messages, { stage: 'Transferência', force: true });
            updateChatContext(chat);
            syncQuickActionButtons(chat);
            renderChatList();
        };
    }

    if (chatCloseBtn) {
        chatCloseBtn.onclick = closeActiveChat;
    }

    if (archiveBtn) {
        archiveBtn.onclick = closeActiveChat;
    }

    if (blockBtn) {
        blockBtn.onclick = () => {
            if (!activeChatJid) return;
            if (confirm('Deseja bloquear este contato?')) {
                alert('Funcionalidade de bloqueio será integrada com a API oficial em breve.');
            }
        };
    }

    // File Upload Listeners
    if (uploadBtnTrigger) {
        uploadBtnTrigger.onclick = () => fileUploadInput.click();
    }
    if (fileUploadInput) {
        fileUploadInput.onchange = (e) => {
            if (e.target.files.length > 0) {
                uploadFiles(Array.from(e.target.files));
            }
        };
    }
    if (filesSelectAll) {
        filesSelectAll.onchange = () => {
            if (filesSelectAll.checked) {
                selectedFileNames = new Set((lastFiles || []).map(f => f && f.name).filter(Boolean));
            } else {
                selectedFileNames = new Set();
            }
            renderFileList(lastFiles || []);
        };
    }
    if (filesDeleteSelectedBtn) {
        filesDeleteSelectedBtn.onclick = deleteSelectedFiles;
    }

    if (saveSettingsBtn) {
        saveSettingsBtn.onclick = saveSettings;
    }

    // Broadcast Handlers
    broadcastTypeRadios.forEach(r => {
        r.onchange = (e) => {
            if (e.target.value === 'file') {
                broadcastTextArea.style.display = 'none';
                broadcastFileArea.style.display = 'block';
            } else {
                broadcastTextArea.style.display = 'block';
                broadcastFileArea.style.display = 'none';
            }
        }
    });

    if (broadcastLocalFileBtn && broadcastLocalFileInput) {
        broadcastLocalFileBtn.onclick = () => broadcastLocalFileInput.click();
        broadcastLocalFileInput.onchange = () => {
            const f = broadcastLocalFileInput.files && broadcastLocalFileInput.files[0];
            if (broadcastLocalFileName) broadcastLocalFileName.textContent = f ? f.name : '';
        };
    }

    if (broadcastFileSourceRadios && broadcastFileSourceRadios.length > 0) {
        broadcastFileSourceRadios.forEach(r => {
            r.onchange = () => {
                const selected = document.querySelector('input[name="broadcast-file-source"]:checked')?.value || 'manager';
                if (broadcastFileSourceManager) broadcastFileSourceManager.style.display = selected === 'manager' ? 'block' : 'none';
                if (broadcastFileSourceLocal) broadcastFileSourceLocal.style.display = selected === 'local' ? 'block' : 'none';
            };
        });
    }

    if (broadcastGroupRefreshBtn) broadcastGroupRefreshBtn.onclick = fetchContactGroups;
    if (broadcastGroupLoadBtn) broadcastGroupLoadBtn.onclick = loadSelectedGroupToLeads;
    if (broadcastGroupSaveBtn) broadcastGroupSaveBtn.onclick = saveLeadsAsGroup;
    if (broadcastGroupDeleteBtn) broadcastGroupDeleteBtn.onclick = deleteSelectedGroup;

    if (broadcastImportCsvBtn && broadcastImportCsvInput) {
        broadcastImportCsvBtn.onclick = () => broadcastImportCsvInput.click();
        broadcastImportCsvInput.onchange = () => {
            const f = broadcastImportCsvInput.files && broadcastImportCsvInput.files[0];
            if (f) importCsvToGroup(f);
            broadcastImportCsvInput.value = '';
        };
    }

    if (contactsGroupRefreshBtn) contactsGroupRefreshBtn.onclick = fetchContactGroups;
    if (contactsGroupCreateBtn) contactsGroupCreateBtn.onclick = createGroupFromSelected;
    if (contactsGroupAddSelectedBtn) contactsGroupAddSelectedBtn.onclick = addSelectedToExistingGroup;
    if (contactsGroupRenameBtn) contactsGroupRenameBtn.onclick = renameSelectedContactsGroup;
    if (contactsGroupDeleteBtn) contactsGroupDeleteBtn.onclick = deleteSelectedContactsGroup;
    if (contactsClearSelectionBtn) contactsClearSelectionBtn.onclick = clearContactsSelection;
    if (contactsGroupSelect) contactsGroupSelect.onchange = loadContactsGroupMembers;

    if (agentFlowsRefreshBtn) agentFlowsRefreshBtn.onclick = fetchAgentFlows;
    if (agentFlowSelect) agentFlowSelect.onchange = fetchAgentRules;
    if (agentFlowActivateBtn) agentFlowActivateBtn.onclick = agentActivateFlow;
    if (agentFlowCreateBtn) agentFlowCreateBtn.onclick = agentCreateFlow;
    if (agentFlowRenameBtn) agentFlowRenameBtn.onclick = agentRenameFlow;
    if (agentFlowDeleteBtn) agentFlowDeleteBtn.onclick = agentDeleteFlow;
    if (agentBootstrapDefaultBtn) agentBootstrapDefaultBtn.onclick = agentBootstrapDefault;
    if (agentRuleAddBtn) agentRuleAddBtn.onclick = agentAddRule;

    if (startBroadcastBtn) startBroadcastBtn.onclick = startBroadcast;

    // Dashboard Action Listeners
    if (dashRestartBtn) dashRestartBtn.onclick = () => handleInstanceAction('restart');
    if (dashLogoutBtn) dashLogoutBtn.onclick = () => handleInstanceAction('logout');

    // Modal Handler
    if (modalClose) modalClose.onclick = () => imageModal.style.display = 'none';
    window.onclick = (e) => { if (e.target === imageModal) imageModal.style.display = 'none'; }

    // Auto-resize textarea
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = messageInput.scrollHeight + 'px';
        const activeChat = chats.find(chat => chat.jid === activeChatJid);
        if (activeChat) {
            renderComposerContext(activeChat, messages);
        }
    });

    // Initial load
    loadSettings();
    startPolling();
    fetchInstanceStatus();
    fetchContactGroups();
    setInterval(fetchInstanceStatus, 10000); // Check status every 10s
});
