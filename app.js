// Data do programa
const START_DATE = new Date('2025-10-13');
const END_DATE = new Date('2026-01-13');

// Treinos de Calistenia por dia
const CALISTHENICS_BY_DAY = {
    0: { // Domingo
        exercises: [
            { name: 'Flexões', sets: '3x15-20', rest: '60s' },
            { name: 'Agachamento Livre', sets: '3x20-25', rest: '60s' },
            { name: 'Prancha', sets: '3x60s', rest: '45s' },
            { name: 'Mountain Climbers', sets: '3x20', rest: '45s' }
        ]
    },
    1: { // Segunda
        exercises: [
            { name: 'Flexões Diamante', sets: '4x10-12', rest: '60s' },
            { name: 'Dips (banco ou paralela)', sets: '4x12-15', rest: '60s' },
            { name: 'Pike Push-ups', sets: '3x10-12', rest: '60s' },
            { name: 'Prancha Lateral', sets: '3x45s cada', rest: '45s' }
        ]
    },
    2: { // Terça
        exercises: [
            { name: 'Burpees', sets: '4x10-12', rest: '60s' },
            { name: 'Jump Squats', sets: '3x15-20', rest: '60s' },
            { name: 'High Knees', sets: '3x30s', rest: '45s' },
            { name: 'Prancha com toque no ombro', sets: '3x20', rest: '45s' }
        ]
    },
    3: { // Quarta
        exercises: [
            { name: 'Pull-ups ou Australian Pull-ups', sets: '4x8-10', rest: '90s' },
            { name: 'Inverted Rows', sets: '3x12-15', rest: '60s' },
            { name: 'Hollow Body Hold', sets: '3x30-45s', rest: '45s' },
            { name: 'Leg Raises', sets: '3x15-20', rest: '45s' }
        ]
    },
    4: { // Quinta
        exercises: [
            { name: 'Pistol Squats (assistido)', sets: '3x8-10 cada', rest: '60s' },
            { name: 'Bulgarian Split Squats', sets: '3x12 cada', rest: '60s' },
            { name: 'Calf Raises', sets: '4x20-25', rest: '45s' },
            { name: 'Wall Sit', sets: '3x45-60s', rest: '60s' }
        ]
    },
    5: { // Sexta
        exercises: [
            { name: 'Archer Push-ups', sets: '3x8-10 cada', rest: '60s' },
            { name: 'Decline Push-ups', sets: '3x12-15', rest: '60s' },
            { name: 'Handstand Hold (parede)', sets: '3x20-30s', rest: '60s' },
            { name: 'L-Sit (progressão)', sets: '3x15-20s', rest: '45s' }
        ]
    },
    6: { // Sábado
        exercises: [
            { name: 'Circuito Full Body:', sets: '3 rounds', rest: '90s entre rounds' },
            { name: '- Flexões', sets: '15 reps', rest: '-' },
            { name: '- Agachamentos', sets: '20 reps', rest: '-' },
            { name: '- Pull-ups', sets: '8 reps', rest: '-' },
            { name: '- Burpees', sets: '10 reps', rest: '-' },
            { name: '- Prancha', sets: '45s', rest: '-' }
        ]
    }
};

// Dados dos treinos por dia da semana (0 = domingo, 1 = segunda, etc.)
const WORKOUTS_BY_DAY = {
    0: { // Domingo
        morning: 'Descanso Total OU Corrida Leve (30-40 min)',
        midday: '-',
        evening: '-',
        count: 'Descanso ou 1 treino leve'
    },
    1: { // Segunda
        morning: 'Musculação: Peito + Tríceps',
        midday: 'Musculação: Ombros + Abdômen',
        evening: '-',
        count: '2 treinos'
    },
    2: { // Terça
        morning: 'Natação: Técnica + Resistência',
        midday: '-',
        evening: '-',
        count: '1 treino'
    },
    3: { // Quarta
        morning: 'Corrida: Intervalado',
        midday: 'Musculação: Costas + Bíceps',
        evening: 'Musculação: Pernas - Posterior',
        count: '3 treinos'
    },
    4: { // Quinta
        morning: 'Natação: Velocidade + Força',
        midday: '-',
        evening: '-',
        count: '1 treino'
    },
    5: { // Sexta
        morning: 'Musculação: Pernas - Anterior',
        midday: 'Musculação: Abdômen + Core',
        evening: '-',
        count: '2 treinos'
    },
    6: { // Sábado
        morning: 'Corrida Longa (60 min) OU Musculação Full Body',
        midday: '-',
        evening: '-',
        count: '1 treino'
    }
};

// Cardápios por tipo de dia
const MEAL_PLANS = {
    '1_treino': [
        { time: '06:00', name: 'Café da Manhã', items: ['1 dose (30g) Whey Protein com 200ml água', '2 fatias pão integral com 1 banana amassada', '2 ovos mexidos'] },
        { time: '08:30', name: 'Pós-Treino', items: ['1 dose Whey Protein', '1 batata doce média (150g) cozida', '1 maçã'] },
        { time: '12:00', name: 'Almoço', items: ['150g frango grelhado', '150g arroz integral', 'Salada verde à vontade + 1 colher sopa azeite', 'Legumes cozidos (brócolis, cenoura)'] },
        { time: '15:00', name: 'Lanche da Tarde', items: ['1 iogurte proteico', '10 amêndoas', '1 colher sopa chia'] },
        { time: '18:00', name: 'Jantar', items: ['150g salmão assado', '120g batata doce', 'Aspargos grelhados'] },
        { time: '22:00', name: 'Ceia (Opcional)', items: ['200ml leite desnatado OU 100g queijo cottage'] }
    ],
    '2_treinos': [
        { time: '06:00', name: 'Café da Manhã', items: ['1 dose Whey Protein com água', '3 fatias pão integral', '2 ovos + 1 clara', '1 banana'] },
        { time: '08:30', name: 'Pós-Treino 1', items: ['1 dose Whey Protein', '200g batata doce', '1 colher sopa pasta amendoim'] },
        { time: '11:30', name: 'Pré-Treino 2 (Almoço)', items: ['150g frango grelhado', '150g arroz integral', 'Salada + legumes'] },
        { time: '14:00', name: 'Pós-Treino 2', items: ['1 dose Whey Protein', '2 bananas', '1 punhado de uvas passas (30g)'] },
        { time: '18:00', name: 'Jantar', items: ['180g carne magra (patinho/lagarto)', '150g batata doce', 'Brócolis e couve-flor'] },
        { time: '22:00', name: 'Ceia', items: ['1 dose caseína OU 150g queijo cottage', '10 nozes'] }
    ],
    '3_treinos': [
        { time: '06:00', name: 'Café da Manhã', items: ['1 dose Whey Protein', '3 fatias pão integral', '2 ovos + 1 clara', '1 banana'] },
        { time: '08:30', name: 'Pós-Treino 1', items: ['1 dose Whey Protein', '200g batata doce', '1 colher sopa pasta amendoim'] },
        { time: '11:30', name: 'Pré-Treino 2 (Almoço)', items: ['150g frango grelhado', '150g arroz integral', 'Salada + legumes'] },
        { time: '14:00', name: 'Pós-Treino 2', items: ['1 dose Whey Protein', '2 bananas', '1 punhado uvas passas'] },
        { time: '17:30', name: 'Pré-Treino 3', items: ['1 iogurte proteico', '10 amêndoas'] },
        { time: '21:00', name: 'Pós-Treino 3 / Jantar', items: ['1 dose Whey Protein OU', '150g peixe grelhado + salada'] },
        { time: '22:00', name: 'Ceia', items: ['100g queijo cottage'] }
    ],
    'domingo': [
        { time: '06:00', name: 'Café da Manhã', items: ['1 dose Whey Protein', '2 fatias pão integral', '2 ovos mexidos', '1 fruta'] },
        { time: '09:00', name: 'Lanche', items: ['1 iogurte proteico', 'Frutas vermelhas'] },
        { time: '12:00', name: 'Almoço', items: ['150g proteína magra', '120g arroz integral', 'Salada + legumes à vontade'] },
        { time: '15:00', name: 'Lanche', items: ['Mix de castanhas (30g)', '1 fruta'] },
        { time: '18:00', name: 'Jantar', items: ['150g peixe ou frango', 'Salada grande', 'Legumes assados'] },
        { time: '21:00', name: 'Ceia (Opcional)', items: ['200ml leite desnatado'] }
    ]
};

// Alongamentos
const STRETCHING_ITEMS = [
    'Peitorais (braço na parede)',
    'Ombros (braço cruzado)',
    'Tríceps (braço atrás da cabeça)',
    'Dorsais (braços estendidos acima)',
    'Quadríceps (puxar pé ao glúteo)',
    'Posteriores (perna estendida)',
    'Glúteos (figura 4)',
    'Panturrilhas (pé na parede)'
];

// Exercícios funcionais
const FUNCTIONAL_ITEMS = [
    'Prancha Frontal - 60s',
    'Prancha Lateral - 30s cada lado',
    'Bird Dog - 10 reps cada lado',
    'Ponte de Glúteo - 15 reps',
    'Superman - 15 reps',
    'Cat-Cow - 10 reps',
    'Rotação Torácica - 10 cada lado',
    'Agachamento Profundo Assistido - 30s'
];

// Checklists
const NUTRITION_CHECKLIST = [
    'Café da manhã às 06:00',
    'Meta proteica atingida',
    '2,5-3,5L de água',
    'Multivitamínico',
    'Cálcio + Vitamina D',
    'Vitamina B12',
    'Whey pós-treino(s)',
    'Creatina 5g'
];

const WORKOUT_CHECKLIST = [
    'Treino manhã (7h) concluído',
    'Treino meio-dia (12h) concluído (se aplicável)',
    'Treino noite (18h) concluído (se aplicável)',
    'Alongamento + funcional realizado',
    'Cargas anotadas'
];

const RECOVERY_CHECKLIST = [
    '7-8 horas de sono',
    'Hidratação adequada',
    'Sem dores anormais'
];

// Estado atual
let currentDate = new Date();

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    initializeDatePicker();
    loadCurrentDay();
    setupEventListeners();
});

function initializeDatePicker() {
    const dateInput = document.getElementById('dateInput');
    const today = new Date();
    
    // Se hoje está dentro do período do programa, usar hoje, senão usar data de início
    if (today >= START_DATE && today <= END_DATE) {
        currentDate = today;
    } else if (today < START_DATE) {
        currentDate = new Date(START_DATE);
    } else {
        currentDate = new Date(END_DATE);
    }
    
    dateInput.value = formatDateForInput(currentDate);
}

function setupEventListeners() {
    document.getElementById('prevDay').addEventListener('click', () => changeDay(-1));
    document.getElementById('nextDay').addEventListener('click', () => changeDay(1));
    document.getElementById('todayBtn').addEventListener('click', goToToday);
    document.getElementById('dateInput').addEventListener('change', onDateChange);
    document.getElementById('saveNotesBtn').addEventListener('click', saveNotes);
    
    // Event listeners para checkboxes
    document.addEventListener('change', (e) => {
        if (e.target.type === 'checkbox') {
            updateProgress();
            saveChecklistState();
        }
    });
}

function changeDay(delta) {
    const newDate = new Date(currentDate);
    newDate.setDate(newDate.getDate() + delta);
    
    if (newDate >= START_DATE && newDate <= END_DATE) {
        currentDate = newDate;
        document.getElementById('dateInput').value = formatDateForInput(currentDate);
        loadCurrentDay();
    }
}

function goToToday() {
    const today = new Date();
    if (today >= START_DATE && today <= END_DATE) {
        currentDate = today;
        document.getElementById('dateInput').value = formatDateForInput(currentDate);
        loadCurrentDay();
    }
}

function onDateChange(e) {
    const selectedDate = new Date(e.target.value + 'T00:00:00');
    if (selectedDate >= START_DATE && selectedDate <= END_DATE) {
        currentDate = selectedDate;
        loadCurrentDay();
    }
}

function loadCurrentDay() {
    const dayNumber = getDayNumber(currentDate);
    const weekNumber = getWeekNumber(currentDate);
    const phase = getPhase(weekNumber);
    const dayOfWeek = currentDate.getDay();
    const workouts = WORKOUTS_BY_DAY[dayOfWeek];
    
    // Atualizar header stats
    document.getElementById('currentDay').textContent = dayNumber;
    document.getElementById('currentPhase').textContent = phase.number;
    document.getElementById('progressPercent').textContent = Math.round((dayNumber / 93) * 100) + '%';
    
    // Atualizar phase banner
    document.getElementById('phaseTitle').textContent = phase.title;
    document.getElementById('phaseDescription').textContent = phase.description;
    document.getElementById('phaseBanner').style.background = phase.color;
    
    // Atualizar resumo
    document.getElementById('displayDate').textContent = formatDateBR(currentDate);
    document.getElementById('displayWeekday').textContent = getWeekdayName(dayOfWeek);
    document.getElementById('displayWorkouts').textContent = workouts.count;
    
    // Calorias e proteínas baseado no número de treinos
    const nutritionInfo = getNutritionInfo(dayOfWeek);
    document.getElementById('displayCalories').textContent = nutritionInfo.calories;
    document.getElementById('displayProtein').textContent = nutritionInfo.protein;
    
    // Carregar alimentação
    loadNutrition(dayOfWeek);
    
    // Carregar treinos
    loadWorkouts(workouts);
    
    // Carregar checklists
    loadChecklists();
    
    // Carregar anotações salvas
    loadSavedNotes();
    
    // Atualizar progresso
    updateProgress();
}

function getDayNumber(date) {
    const diffTime = date - START_DATE;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays + 1;
}

function getWeekNumber(date) {
    const dayNumber = getDayNumber(date);
    return Math.ceil(dayNumber / 7);
}

function getPhase(weekNumber) {
    if (weekNumber <= 4) {
        return {
            number: 1,
            title: 'FASE 1: FUNDAÇÃO',
            description: 'Adaptação e Técnica',
            color: 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
        };
    } else if (weekNumber <= 8) {
        return {
            number: 2,
            title: 'FASE 2: HIPERTROFIA E INTENSIFICAÇÃO',
            description: 'Aumento de Volume Muscular',
            color: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
        };
    } else {
        return {
            number: 3,
            title: 'FASE 3: DEFINIÇÃO E PICO',
            description: 'Máxima Definição e Queima de Gordura',
            color: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
        };
    }
}

function getNutritionInfo(dayOfWeek) {
    if (dayOfWeek === 0) { // Domingo
        return { calories: '1.900-1.950 kcal', protein: '150-155g' };
    } else if (dayOfWeek === 3) { // Quarta (3 treinos)
        return { calories: '2.400-2.500 kcal', protein: '165-175g' };
    } else if (dayOfWeek === 1 || dayOfWeek === 5) { // Segunda e Sexta (2 treinos)
        return { calories: '2.300-2.400 kcal', protein: '165-175g' };
    } else { // Demais dias (1 treino)
        return { calories: '2.050-2.100 kcal', protein: '155-165g' };
    }
}

function loadNutrition(dayOfWeek) {
    let mealPlan;
    if (dayOfWeek === 0) {
        mealPlan = MEAL_PLANS.domingo;
    } else if (dayOfWeek === 3) {
        mealPlan = MEAL_PLANS['3_treinos'];
    } else if (dayOfWeek === 1 || dayOfWeek === 5) {
        mealPlan = MEAL_PLANS['2_treinos'];
    } else {
        mealPlan = MEAL_PLANS['1_treino'];
    }
    
    const container = document.getElementById('nutritionContent');
    container.innerHTML = mealPlan.map(meal => `
        <div class="meal-card">
            <div class="meal-time">${meal.time} - ${meal.name}</div>
            <ul class="meal-items">
                ${meal.items.map(item => `<li>${item}</li>`).join('')}
            </ul>
        </div>
    `).join('');
}

function loadWorkouts(workouts) {
    const container = document.getElementById('workoutsContent');
    const dayOfWeek = currentDate.getDay();
    const calisthenics = CALISTHENICS_BY_DAY[dayOfWeek];
    
    const workoutTimes = [
        { time: '07:00', label: 'Treino Manhã', type: workouts.morning },
        { time: '12:00', label: 'Treino Meio-Dia', type: workouts.midday },
        { time: '18:00-19:00', label: 'Treino Noite', type: workouts.evening }
    ];
    
    let html = workoutTimes.map(workout => `
        <div class="workout-card">
            <div class="workout-time">${workout.time} - ${workout.label}</div>
            <div class="workout-type">${workout.type}</div>
        </div>
    `).join('');
    
    // Adicionar calistenia
    html += `
        <div class="workout-card calisthenics-card">
            <div class="workout-time">🤸 Calistenia Diária (15-20 min)</div>
            <div class="workout-type">Pode ser feita em qualquer horário do dia</div>
            <div class="calisthenics-exercises">
                ${calisthenics.exercises.map(ex => `
                    <div class="exercise-item">
                        <span class="exercise-name">${ex.name}</span>
                        <span class="exercise-sets">${ex.sets}</span>
                        <span class="exercise-rest">Descanso: ${ex.rest}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function loadChecklists() {
    // Alongamentos
    const stretchingContainer = document.getElementById('stretchingChecklist');
    stretchingContainer.innerHTML = STRETCHING_ITEMS.map((item, index) => `
        <div class="checklist-item">
            <input type="checkbox" id="stretch_${index}" data-list="stretching">
            <label for="stretch_${index}">${item}</label>
        </div>
    `).join('');
    
    // Funcionais
    const functionalContainer = document.getElementById('functionalChecklist');
    functionalContainer.innerHTML = FUNCTIONAL_ITEMS.map((item, index) => `
        <div class="checklist-item">
            <input type="checkbox" id="functional_${index}" data-list="functional">
            <label for="functional_${index}">${item}</label>
        </div>
    `).join('');
    
    // Nutrição
    const nutritionChecklistContainer = document.getElementById('nutritionChecklist');
    nutritionChecklistContainer.innerHTML = NUTRITION_CHECKLIST.map((item, index) => `
        <div class="checklist-item">
            <input type="checkbox" id="nutrition_${index}" data-list="nutrition">
            <label for="nutrition_${index}">${item}</label>
        </div>
    `).join('');
    
    // Treino
    const workoutChecklistContainer = document.getElementById('workoutChecklist');
    workoutChecklistContainer.innerHTML = WORKOUT_CHECKLIST.map((item, index) => `
        <div class="checklist-item">
            <input type="checkbox" id="workout_${index}" data-list="workout">
            <label for="workout_${index}">${item}</label>
        </div>
    `).join('');
    
    // Recuperação
    const recoveryChecklistContainer = document.getElementById('recoveryChecklist');
    recoveryChecklistContainer.innerHTML = RECOVERY_CHECKLIST.map((item, index) => `
        <div class="checklist-item">
            <input type="checkbox" id="recovery_${index}" data-list="recovery">
            <label for="recovery_${index}">${item}</label>
        </div>
    `).join('');
    
    // Carregar estado dos checkboxes
    loadChecklistState();
}

function updateProgress() {
    const allCheckboxes = document.querySelectorAll('input[type="checkbox"]');
    const checkedCheckboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    const progress = allCheckboxes.length > 0 ? (checkedCheckboxes.length / allCheckboxes.length) * 100 : 0;
    
    const progressBar = document.getElementById('dailyProgress');
    const progressText = document.getElementById('progressText');
    
    progressBar.style.setProperty('--progress-width', progress + '%');
    progressText.textContent = Math.round(progress) + '% concluído';
    
    // Atualizar classes dos itens
    allCheckboxes.forEach(checkbox => {
        const item = checkbox.closest('.checklist-item');
        if (checkbox.checked) {
            item.classList.add('checked');
        } else {
            item.classList.remove('checked');
        }
    });
}

function saveChecklistState() {
    const dateKey = formatDateForInput(currentDate);
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    const state = {};
    
    checkboxes.forEach(checkbox => {
        state[checkbox.id] = checkbox.checked;
    });
    
    localStorage.setItem(`checklist_${dateKey}`, JSON.stringify(state));
}

function loadChecklistState() {
    const dateKey = formatDateForInput(currentDate);
    const savedState = localStorage.getItem(`checklist_${dateKey}`);
    
    if (savedState) {
        const state = JSON.parse(savedState);
        Object.keys(state).forEach(id => {
            const checkbox = document.getElementById(id);
            if (checkbox) {
                checkbox.checked = state[id];
            }
        });
    }
}

function saveNotes() {
    const dateKey = formatDateForInput(currentDate);
    const notes = {
        weight: document.getElementById('weightInput').value,
        cardioTime: document.getElementById('cardioTimeInput').value,
        swimDistance: document.getElementById('swimDistanceInput').value,
        energy: document.getElementById('energySelect').value,
        recovery: document.getElementById('recoverySelect').value,
        hunger: document.getElementById('hungerSelect').value,
        observations: document.getElementById('observationsText').value
    };
    
    localStorage.setItem(`notes_${dateKey}`, JSON.stringify(notes));
    showSuccessMessage('Anotações salvas com sucesso! ✅');
}

function loadSavedNotes() {
    const dateKey = formatDateForInput(currentDate);
    const savedNotes = localStorage.getItem(`notes_${dateKey}`);
    
    if (savedNotes) {
        const notes = JSON.parse(savedNotes);
        document.getElementById('weightInput').value = notes.weight || '';
        document.getElementById('cardioTimeInput').value = notes.cardioTime || '';
        document.getElementById('swimDistanceInput').value = notes.swimDistance || '';
        document.getElementById('energySelect').value = notes.energy || '';
        document.getElementById('recoverySelect').value = notes.recovery || '';
        document.getElementById('hungerSelect').value = notes.hunger || '';
        document.getElementById('observationsText').value = notes.observations || '';
    } else {
        // Limpar campos
        document.getElementById('weightInput').value = '';
        document.getElementById('cardioTimeInput').value = '';
        document.getElementById('swimDistanceInput').value = '';
        document.getElementById('energySelect').value = '';
        document.getElementById('recoverySelect').value = '';
        document.getElementById('hungerSelect').value = '';
        document.getElementById('observationsText').value = '';
    }
}

function showSuccessMessage(message) {
    const messageEl = document.createElement('div');
    messageEl.className = 'success-message';
    messageEl.textContent = message;
    document.body.appendChild(messageEl);
    
    setTimeout(() => {
        messageEl.remove();
    }, 3000);
}

// Funções auxiliares
function formatDateForInput(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function formatDateBR(date) {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
}

function getWeekdayName(dayOfWeek) {
    const days = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado'];
    return days[dayOfWeek];
}

