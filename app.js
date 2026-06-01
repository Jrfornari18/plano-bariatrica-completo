/* =============================================
   SOUL WAKE - MyAppFit.pro
   JavaScript Principal
   ============================================= */

// ---- State ----
const state = {
    currentStep: 0,
    totalSteps: 5,
    selectedGoals: [],
    selectedDiet: 'omnivore',
    userName: '',
    currentSection: 'home',
    waterCount: 0,
    dayCount: 1,
    streak: 0,
    checklistProgress: 0,
    scanBodyHistory: [],
    currentCyclePhase: null,
    currentMood: null
};

// ---- Quotes ----
const quotes = [
    '"Cada respiração consciente é um ato de amor próprio."',
    '"O corpo guarda o que a mente não entende e libera quando a alma desperta."',
    '"Movimento com consciência transforma não só o corpo, mas a vida."',
    '"Você não precisa ser perfeita para começar. Comece para se tornar."',
    '"A quietude não é ausência de movimento. É presença total."',
    '"Cuide do seu corpo. É o único lugar onde você tem que viver."',
    '"Yoga não é sobre tocar os pés. É sobre o que você aprende no caminho."',
    '"Respire fundo. Você já chegou onde precisa estar agora."',
    '"A força não vem da capacidade física. Vem de uma vontade indomável."',
    '"Seu bem-estar é um ato revolucionário de autocuidado."'
];

// ---- Meal Plans ----
const mealPlans = {
    omnivore: [
        { icon: '🌅', label: 'Café da Manhã', hour: '07:00', name: 'Bowl de Açaí com Granola Artesanal', desc: 'Açaí orgânico, banana, morango, granola sem açúcar, mel e chia.', macros: ['🔥 380 kcal', '🥩 12g prot', '🌾 48g carb', '🫒 14g gordura'] },
        { icon: '🍎', label: 'Lanche da Manhã', hour: '10:00', name: 'Maçã + Pasta de Amendoim Natural', desc: 'Maçã fatiada com 2 colheres de pasta de amendoim sem adição de açúcar.', macros: ['🔥 220 kcal', '🥩 6g prot', '🌾 28g carb', '🫒 10g gordura'] },
        { icon: '☀️', label: 'Almoço', hour: '12:30', name: 'Bowl Mediterrâneo de Frango', desc: 'Frango grelhado, quinoa, tomate cereja, pepino, azeitonas, feta e azeite extra virgem.', macros: ['🔥 520 kcal', '🥩 42g prot', '🌾 38g carb', '🫒 18g gordura'] },
        { icon: '🌿', label: 'Lanche da Tarde', hour: '15:30', name: 'Smoothie Verde Detox', desc: 'Espinafre, banana congelada, leite de amêndoas, proteína vegetal e gengibre.', macros: ['🔥 180 kcal', '🥩 15g prot', '🌾 22g carb', '🫒 4g gordura'] },
        { icon: '🌙', label: 'Jantar', hour: '19:00', name: 'Salmão ao Forno com Legumes Assados', desc: 'Salmão selvagem, batata-doce, brócolis e cenoura assados com ervas aromáticas.', macros: ['🔥 480 kcal', '🥩 38g prot', '🌾 32g carb', '🫒 16g gordura'] },
        { icon: '⭐', label: 'Ceia (opcional)', hour: '21:00', name: 'Iogurte Grego com Mel e Nozes', desc: 'Iogurte grego natural, fio de mel orgânico e mix de nozes.', macros: ['🔥 160 kcal', '🥩 12g prot', '🌾 14g carb', '🫒 6g gordura'] }
    ],
    vegetarian: [
        { icon: '🌅', label: 'Café da Manhã', hour: '07:00', name: 'Panquecas de Aveia com Frutas Vermelhas', desc: 'Panquecas de aveia e banana, calda de frutas vermelhas e iogurte natural.', macros: ['🔥 360 kcal', '🥩 14g prot', '🌾 52g carb', '🫒 10g gordura'] },
        { icon: '🍎', label: 'Lanche da Manhã', hour: '10:00', name: 'Queijo Cottage com Frutas', desc: 'Cottage cremoso com morangos frescos, kiwi e sementes de linhaça.', macros: ['🔥 190 kcal', '🥩 16g prot', '🌾 18g carb', '🫒 5g gordura'] },
        { icon: '☀️', label: 'Almoço', hour: '12:30', name: 'Risoto de Cogumelos e Ervas Finas', desc: 'Arroz arbóreo, mix de cogumelos, parmesão, vinho branco e ervas frescas.', macros: ['🔥 490 kcal', '🥩 18g prot', '🌾 62g carb', '🫒 14g gordura'] },
        { icon: '🌿', label: 'Lanche da Tarde', hour: '15:30', name: 'Hummus com Palitos de Legumes', desc: 'Hummus caseiro de grão-de-bico com cenoura, pepino e pimentão colorido.', macros: ['🔥 210 kcal', '🥩 8g prot', '🌾 24g carb', '🫒 10g gordura'] },
        { icon: '🌙', label: 'Jantar', hour: '19:00', name: 'Curry de Lentilha com Arroz Integral', desc: 'Lentilha vermelha, leite de coco, curry, cúrcuma, coentro e arroz integral.', macros: ['🔥 460 kcal', '🥩 22g prot', '🌾 58g carb', '🫒 12g gordura'] },
        { icon: '⭐', label: 'Ceia (opcional)', hour: '21:00', name: 'Chá de Camomila + Tâmaras', desc: 'Chá de camomila quente com 3 tâmaras recheadas com pasta de amêndoas.', macros: ['🔥 120 kcal', '🥩 2g prot', '🌾 20g carb', '🫒 4g gordura'] }
    ],
    vegan: [
        { icon: '🌅', label: 'Café da Manhã', hour: '07:00', name: 'Overnight Oats com Leite de Aveia', desc: 'Aveia, leite de aveia, chia, banana, manteiga de amendoim e cacau nibs.', macros: ['🔥 380 kcal', '🥩 12g prot', '🌾 54g carb', '🫒 12g gordura'] },
        { icon: '🍎', label: 'Lanche da Manhã', hour: '10:00', name: 'Mix de Frutas Secas e Sementes', desc: 'Tâmaras, damascos, castanhas, sementes de abóbora e cranberry.', macros: ['🔥 200 kcal', '🥩 5g prot', '🌾 28g carb', '🫒 8g gordura'] },
        { icon: '☀️', label: 'Almoço', hour: '12:30', name: 'Buddha Bowl Colorido', desc: 'Grão-de-bico assado, quinoa, beterraba, abacate, cenoura e tahine.', macros: ['🔥 520 kcal', '🥩 20g prot', '🌾 58g carb', '🫒 20g gordura'] },
        { icon: '🌿', label: 'Lanche da Tarde', hour: '15:30', name: 'Smoothie de Proteína Vegetal', desc: 'Proteína de ervilha, leite de amêndoas, espinafre, banana e gengibre.', macros: ['🔥 220 kcal', '🥩 20g prot', '🌾 24g carb', '🫒 4g gordura'] },
        { icon: '🌙', label: 'Jantar', hour: '19:00', name: 'Tofu Grelhado com Legumes Salteados', desc: 'Tofu firme marinado, brócolis, cogumelos, pimentão e arroz integral.', macros: ['🔥 440 kcal', '🥩 24g prot', '🌾 46g carb', '🫒 14g gordura'] },
        { icon: '⭐', label: 'Ceia (opcional)', hour: '21:00', name: 'Golden Milk Vegano', desc: 'Leite de coco, cúrcuma, canela, pimenta-do-reino e mel de agave.', macros: ['🔥 130 kcal', '🥩 2g prot', '🌾 16g carb', '🫒 6g gordura'] }
    ],
    functional: [
        { icon: '🌅', label: 'Café da Manhã', hour: '07:00', name: 'Omelete Funcional Anti-inflamatório', desc: 'Ovos caipiras, cúrcuma, espinafre, tomate, azeite e sementes de chia.', macros: ['🔥 340 kcal', '🥩 24g prot', '🌾 12g carb', '🫒 22g gordura'] },
        { icon: '🍎', label: 'Lanche da Manhã', hour: '10:00', name: 'Kefir com Frutas Vermelhas', desc: 'Kefir de leite, mix de frutas vermelhas, mel e sementes de linhaça.', macros: ['🔥 180 kcal', '🥩 10g prot', '🌾 22g carb', '🫒 5g gordura'] },
        { icon: '☀️', label: 'Almoço', hour: '12:30', name: 'Tigela Anti-inflamatória', desc: 'Salmão, quinoa preta, abacate, cúrcuma, gengibre, couve e azeite.', macros: ['🔥 560 kcal', '🥩 40g prot', '🌾 36g carb', '🫒 24g gordura'] },
        { icon: '🌿', label: 'Lanche da Tarde', hour: '15:30', name: 'Matcha Latte + Castanhas', desc: 'Matcha ceremonial, leite de aveia, mix de castanhas e amêndoas.', macros: ['🔥 240 kcal', '🥩 8g prot', '🌾 18g carb', '🫒 16g gordura'] },
        { icon: '🌙', label: 'Jantar', hour: '19:00', name: 'Frango com Caldo de Osso e Legumes', desc: 'Frango orgânico, caldo de osso, batata-doce, brócolis e ervas.', macros: ['🔥 480 kcal', '🥩 44g prot', '🌾 28g carb', '🫒 14g gordura'] },
        { icon: '⭐', label: 'Ceia (opcional)', hour: '21:00', name: 'Chá de Ashwagandha + Mel', desc: 'Chá adaptogênico de ashwagandha com mel cru e canela.', macros: ['🔥 60 kcal', '🥩 0g prot', '🌾 14g carb', '🫒 0g gordura'] }
    ]
};

// ---- Recipes ----
const recipes = [
    { emoji: '🥗', name: 'Buddha Bowl Arco-Íris', desc: 'Bowl colorido e nutritivo com grãos, vegetais frescos e molho tahine.', tags: ['🌱 Vegana', '⏱️ 25 min', '🌾 Sem glúten'] },
    { emoji: '🍵', name: 'Golden Milk Soul Wake', desc: 'Bebida dourada anti-inflamatória com cúrcuma, canela e leite vegetal.', tags: ['🌱 Vegana', '⏱️ 5 min', '💛 Anti-inflamatório'] },
    { emoji: '🥤', name: 'Smoothie Verde Detox', desc: 'Espinafre, pepino, maçã verde, limão e gengibre para desintoxicar.', tags: ['🌱 Vegana', '⏱️ 5 min', '🍃 Detox'] },
    { emoji: '🍲', name: 'Curry de Grão-de-Bico', desc: 'Curry cremoso com leite de coco, especiarias e grão-de-bico.', tags: ['🌱 Vegana', '⏱️ 35 min', '🌶️ Especiado'] },
    { emoji: '🥞', name: 'Panquecas de Banana e Aveia', desc: 'Panquecas sem farinha, apenas banana, aveia e ovo. Simples e deliciosas.', tags: ['🥚 Vegetariana', '⏱️ 15 min', '💪 Proteica'] },
    { emoji: '🫙', name: 'Overnight Oats de Maracujá', desc: 'Aveia preparada na noite anterior com leite vegetal e polpa de maracujá.', tags: ['🌱 Vegana', '⏱️ 5 min', '🌙 Preparo noturno'] }
];

// ---- Practice Content ----
const practiceContent = {
    'yoga-morning': {
        title: '🧘‍♀️ Despertar Matinal',
        duration: '25 min', level: 'Iniciante',
        description: 'Uma sequência gentil para acordar o corpo com consciência e gratidão.',
        steps: [
            { name: 'Respiração Inicial', duration: '3 min', desc: 'Sente-se confortavelmente. Feche os olhos. Respire profundamente 5 vezes.' },
            { name: 'Gato-Vaca (Marjaryasana)', duration: '3 min', desc: 'Em quatro apoios, alterne entre arquear e curvar a coluna. Sincronize com a respiração.' },
            { name: 'Cachorro Olhando para Baixo', duration: '3 min', desc: 'Eleve os quadris, alongue a coluna. Mantenha os joelhos levemente dobrados.' },
            { name: 'Guerreira I e II', duration: '6 min', desc: 'Sequência de guerreiras para ativar força e estabilidade. 3 min de cada lado.' },
            { name: 'Postura da Criança (Balasana)', duration: '3 min', desc: 'Descanso profundo. Testa no chão, braços estendidos. Respire para as costas.' },
            { name: 'Torção Suave', duration: '4 min', desc: 'Deitada, leve os joelhos para cada lado. Libere tensões na coluna lombar.' },
            { name: 'Savasana', duration: '3 min', desc: 'Deite-se completamente. Relaxe cada parte do corpo. Integre a prática.' }
        ]
    },
    'yoga-night': {
        title: '🌙 Yoga Noturno',
        duration: '30 min', level: 'Todos os níveis',
        description: 'Sequência restaurativa para soltar as tensões do dia e preparar para o sono.',
        steps: [
            { name: 'Respiração 4-7-8', duration: '5 min', desc: 'Inspire por 4 tempos, segure por 7, expire por 8. Repita 5 vezes.' },
            { name: 'Pernas na Parede', duration: '5 min', desc: 'Deite próxima à parede e eleve as pernas. Excelente para circulação.' },
            { name: 'Borboleta Reclinada', duration: '5 min', desc: 'Deitada, junte as plantas dos pés. Deixe os joelhos abrirem naturalmente.' },
            { name: 'Torção Supina', duration: '6 min', desc: 'Leve os joelhos para cada lado. 3 min de cada lado.' },
            { name: 'Postura do Bebê Feliz', duration: '4 min', desc: 'Segure os pés e balance suavemente. Libera quadril e lombar.' },
            { name: 'Savasana com Visualização', duration: '5 min', desc: 'Relaxamento profundo com visualização de um lugar seguro e tranquilo.' }
        ]
    },
    'yoga-power': {
        title: '🔥 Vinyasa Power',
        duration: '45 min', level: 'Intermediário',
        description: 'Fluxo dinâmico para ativar energia, construir força e aguçar o foco mental.',
        steps: [
            { name: 'Aquecimento Dinâmico', duration: '5 min', desc: 'Rotações de pescoço, ombros, quadril. Prepare as articulações.' },
            { name: 'Saudação ao Sol A', duration: '8 min', desc: '5 repetições. Sincronize movimento e respiração.' },
            { name: 'Saudação ao Sol B', duration: '8 min', desc: '3 repetições com guerreiras. Construa calor interno.' },
            { name: 'Sequência de Equilíbrio', duration: '10 min', desc: 'Árvore, Guerreira III, Meia Lua. Desafie seu equilíbrio.' },
            { name: 'Inversões Suaves', duration: '7 min', desc: 'Cachorro olhando para baixo, Golfinho.' },
            { name: 'Resfriamento', duration: '7 min', desc: 'Alongamentos profundos. Pigeon pose, torções, flexões frontais.' }
        ]
    },
    'yin-yoga': {
        title: '💆‍♀️ Yin Yoga - Soltar',
        duration: '40 min', level: 'Restaurativo',
        description: 'Posturas passivas de longa duração para liberar tensões profundas e emoções guardadas.',
        steps: [
            { name: 'Borboleta', duration: '5 min', desc: 'Sente-se com plantas dos pés juntas. Deixe o corpo dobrar para frente.' },
            { name: 'Dragão', duration: '6 min', desc: 'Lunge profundo. 3 min de cada lado. Abre quadril e flexores.' },
            { name: 'Cisne (Pigeon)', duration: '8 min', desc: 'Abertura profunda de quadril. 4 min de cada lado.' },
            { name: 'Lagarta', duration: '5 min', desc: 'Flexão frontal sentada. Deixe a coluna arredondar naturalmente.' },
            { name: 'Torção Yin', duration: '6 min', desc: 'Torção suave deitada. 3 min de cada lado.' },
            { name: 'Savasana Yin', duration: '10 min', desc: 'Relaxamento profundo final. Integre todas as liberações.' }
        ]
    },
    'breath-478': {
        title: '🌬️ Respiração 4-7-8',
        duration: '10 min', level: 'Todos os níveis',
        description: 'Técnica para acalmar o sistema nervoso e reduzir ansiedade rapidamente.',
        steps: [
            { name: 'Posição', duration: '1 min', desc: 'Sente-se confortavelmente. Língua atrás dos dentes superiores.' },
            { name: 'Expire completamente', duration: '1 min', desc: 'Expire todo o ar pela boca com um som suave.' },
            { name: 'Ciclo 4-7-8', duration: '6 min', desc: 'Inspire 4 tempos. Segure 7. Expire 8. Repita 8 vezes.' },
            { name: 'Integração', duration: '2 min', desc: 'Retorne à respiração natural. Observe a calma instalada.' }
        ]
    },
    'breath-kapalabhati': {
        title: '⚡ Kapalabhati - Energia',
        duration: '8 min', level: 'Intermediário',
        description: 'Respiração de fogo para limpar os pulmões e energizar o corpo.',
        steps: [
            { name: 'Preparação', duration: '2 min', desc: 'Sente-se com coluna ereta. Respire profundamente.' },
            { name: 'Kapalabhati Lento', duration: '2 min', desc: 'Expirações curtas e forçadas. 1 por segundo. 60 repetições.' },
            { name: 'Kapalabhati Rápido', duration: '2 min', desc: '2 por segundo. 120 repetições.' },
            { name: 'Retenção', duration: '2 min', desc: 'Inspire fundo, segure 15s. Expire lento. Repita 3 vezes.' }
        ]
    },
    'breath-ujjayi': {
        title: '🌊 Respiração Ujjayi',
        duration: '5 min', level: 'Iniciante',
        description: 'A respiração oceânica do yoga para manter foco durante a prática.',
        steps: [
            { name: 'Aprender o Som', duration: '2 min', desc: 'Expire como se embaçasse um espelho. Feche a boca mantendo a constrição.' },
            { name: 'Praticar', duration: '3 min', desc: 'Inspire e expire pelo nariz com o som suave do oceano. 10 ciclos.' }
        ]
    },
    'stretch-neck': {
        title: '🌺 Liberar Tensão Cervical',
        duration: '12 min', level: 'Todos os níveis',
        description: 'Alívio de dores no pescoço e ombros causadas por horas no computador.',
        steps: [
            { name: 'Rotação de Pescoço', duration: '2 min', desc: 'Gire lentamente o pescoço para cada lado. 5 rotações.' },
            { name: 'Inclinação Lateral', duration: '3 min', desc: 'Orelha ao ombro. 30 segundos de cada lado. 3 vezes.' },
            { name: 'Rotação de Ombros', duration: '2 min', desc: '10 rotações para frente e 10 para trás.' },
            { name: 'Abertura de Peito', duration: '3 min', desc: 'Dedos entrelaçados atrás. Abra o peito e eleve o olhar.' },
            { name: 'Automassagem', duration: '2 min', desc: 'Massageie o pescoço e base do crânio com as pontas dos dedos.' }
        ]
    },
    'stretch-hip': {
        title: '🌸 Abertura de Quadril',
        duration: '20 min', level: 'Todos os níveis',
        description: 'O quadril guarda emoções. Esta sequência libera tensões físicas e emocionais.',
        steps: [
            { name: 'Aquecimento', duration: '3 min', desc: 'Rotações suaves de quadril em pé. 10 para cada lado.' },
            { name: 'Lunge Baixo', duration: '4 min', desc: 'Joelho no chão, afunde o quadril. 2 min de cada lado.' },
            { name: 'Pigeon Pose', duration: '6 min', desc: 'Postura do pombo. 3 min de cada lado.' },
            { name: 'Borboleta', duration: '4 min', desc: 'Plantas dos pés juntas, joelhos abertos. Incline suavemente.' },
            { name: 'Savasana', duration: '3 min', desc: 'Integre as liberações. Permita que emoções surjam e passem.' }
        ]
    },
    'corporate-pause': {
        title: '💼 Pausa Consciente 5 min',
        duration: '5 min', level: 'Escritório',
        description: 'Micro-prática para fazer na cadeira. Recentre e volte com mais foco.',
        steps: [
            { name: 'Parar e Perceber', duration: '1 min', desc: 'Pare o que está fazendo. Sente-se bem. Feche os olhos.' },
            { name: 'Respiração Quadrada', duration: '2 min', desc: 'Inspire 4, segure 4, expire 4, segure 4. Repita 6 vezes.' },
            { name: 'Alongamento na Cadeira', duration: '1 min', desc: 'Eleve os braços, torça para cada lado, role os ombros.' },
            { name: 'Intenção', duration: '1 min', desc: 'Defina uma intenção para as próximas horas. Abra os olhos.' }
        ]
    },
    'corporate-team': {
        title: '🤝 Soul Wake em Equipe',
        duration: '60-90 min', level: 'Grupo',
        description: 'Programa corporativo para equipes. Movimento, respiração e conexão.',
        steps: [
            { name: 'Check-in Coletivo', duration: '10 min', desc: 'Cada participante compartilha uma palavra sobre como está chegando.' },
            { name: 'Aquecimento em Grupo', duration: '15 min', desc: 'Movimentos sincronizados, respiração coletiva.' },
            { name: 'Prática Principal', duration: '30 min', desc: 'Yoga flow adaptado, respiratórios e alongamentos em duplas.' },
            { name: 'Meditação Guiada', duration: '15 min', desc: 'Meditação de visualização para foco e criatividade.' },
            { name: 'Check-out', duration: '10 min', desc: 'Compartilhamento de insights. Intenção coletiva.' }
        ]
    }
};

// ---- Cycle Phase Recommendations ----
const cycleRecommendations = {
    menstrual: { title: 'Fase Menstrual 🌑', practice: 'Yoga Restaurativo, Yin Yoga, meditação suave', nutrition: 'Alimentos ricos em ferro: lentilha, espinafre, beterraba. Chá de framboesa.', energy: 'Priorize descanso e introspecção. Evite treinos intensos.', affirmation: '"Honro meu ciclo. Descanso é produtivo."' },
    follicular: { title: 'Fase Folicular 🌒', practice: 'Yoga dinâmico, Vinyasa, novos desafios', nutrition: 'Proteínas leves, vegetais frescos, sementes de linhaça e abóbora.', energy: 'Energia crescente. Ótimo para iniciar projetos e práticas novas.', affirmation: '"Estou florescendo. Abraço o novo com entusiasmo."' },
    ovulatory: { title: 'Fase Ovulatória 🌕', practice: 'Power Yoga, práticas em grupo, desafios físicos', nutrition: 'Alimentos anti-inflamatórios, frutas coloridas, vegetais crucíferos.', energy: 'Pico de energia e sociabilidade. Aproveite para práticas intensas.', affirmation: '"Estou no meu pico. Brilho e conecto."' },
    luteal: { title: 'Fase Lútea 🌘', practice: 'Yoga suave, alongamentos, práticas introspectivas', nutrition: 'Magnésio (chocolate amargo, abacate), carboidratos complexos, camomila.', energy: 'Volte para dentro. Cuide-se com gentileza.', affirmation: '"Cuido de mim com amor. Minha sensibilidade é um presente."' }
};

// ---- Mood Recommendations ----
const moodRecommendations = {
    amazing: '✨ Que energia incrível! Aproveite para fazer o Vinyasa Power ou uma prática mais desafiadora hoje.',
    good: '🙂 Ótimo estado! Siga o programa regular com presença e gratidão.',
    neutral: '😐 Dias neutros pedem práticas suaves. Que tal um Yin Yoga ou respiração 4-7-8?',
    tired: '😔 Seu corpo pede cuidado. Uma Pausa Consciente de 5 min e um chá de camomila podem ajudar.',
    stressed: '😤 Respire. A respiração 4-7-8 é perfeita agora. Depois, um Yoga Noturno para soltar as tensões.'
};

// =============================================
// ONBOARDING
// =============================================

function nextStep() {
    const currentStepEl = document.getElementById('step-' + state.currentStep);
    currentStepEl.classList.remove('active');
    state.currentStep++;
    if (state.currentStep >= state.totalSteps) { completeOnboarding(); return; }
    document.getElementById('step-' + state.currentStep).classList.add('active');
}

function prevStep() {
    if (state.currentStep === 0) return;
    document.getElementById('step-' + state.currentStep).classList.remove('active');
    state.currentStep--;
    document.getElementById('step-' + state.currentStep).classList.add('active');
}

function toggleGoal(el, goal) {
    el.classList.toggle('selected');
    const idx = state.selectedGoals.indexOf(goal);
    if (idx === -1) { state.selectedGoals.push(goal); } else { state.selectedGoals.splice(idx, 1); }
}

function selectDiet(el, diet) {
    document.querySelectorAll('.diet-card').forEach(function(c) { c.classList.remove('selected'); });
    el.classList.add('selected');
    state.selectedDiet = diet;
}

function completeOnboarding() {
    state.userName = document.getElementById('userName') ? document.getElementById('userName').value || 'Guerreira' : 'Guerreira';
    localStorage.setItem('sw_userName', state.userName);
    localStorage.setItem('sw_diet', state.selectedDiet);
    localStorage.setItem('sw_onboarded', 'true');
    localStorage.setItem('sw_startDate', new Date().toISOString());
    document.getElementById('greetingName').textContent = state.userName;
    document.getElementById('onboardingOverlay').classList.remove('active');
    document.getElementById('onboardingOverlay').classList.add('hidden');
    document.getElementById('mainApp').classList.remove('hidden');
    initApp();
    showToast('Bem-vinda, ' + state.userName + '! 🌿');
}

// =============================================
// APP INIT
// =============================================

function initApp() {
    var savedName = localStorage.getItem('sw_userName');
    var savedDiet = localStorage.getItem('sw_diet') || 'omnivore';
    var startDate = localStorage.getItem('sw_startDate');

    if (savedName) {
        state.userName = savedName;
        document.getElementById('greetingName').textContent = savedName;
    }
    state.selectedDiet = savedDiet;

    if (startDate) {
        var start = new Date(startDate);
        var now = new Date();
        var diff = Math.floor((now - start) / (1000 * 60 * 60 * 24)) + 1;
        state.dayCount = diff;
        document.getElementById('homeDay').textContent = diff;
    }

    var randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
    document.getElementById('dailyQuote').textContent = randomQuote;

    initWaterTracker();
    renderMealPlan(savedDiet);
    renderRecipes();
}

// =============================================
// NAVIGATION
// =============================================

function showSection(section) {
    document.querySelectorAll('.app-section').forEach(function(s) { s.classList.remove('active'); });
    document.querySelectorAll('.nav-item').forEach(function(n) { n.classList.remove('active'); });
    document.getElementById('section-' + section).classList.add('active');
    document.getElementById('nav-' + section).classList.add('active');
    state.currentSection = section;
}

// =============================================
// HOME
// =============================================

function updateProgress() {
    var checkboxes = document.querySelectorAll('#homeChecklist input[type="checkbox"]');
    var total = checkboxes.length;
    var checked = 0;
    checkboxes.forEach(function(cb) { if (cb.checked) checked++; });
    var percent = Math.round((checked / total) * 100);
    state.checklistProgress = percent;
    document.getElementById('dailyProgressBar').style.width = percent + '%';
    document.getElementById('progressText').textContent = checked + ' de ' + total + ' concluídas';
    document.getElementById('homeProgress').textContent = percent + '%';
    if (percent === 100) {
        showToast('🎉 Parabéns! Checklist completo!');
        state.streak++;
        document.getElementById('homeStreak').textContent = state.streak;
    }
}

function setMood(el, mood) {
    document.querySelectorAll('.mood-btn').forEach(function(b) { b.classList.remove('selected'); });
    el.classList.add('selected');
    state.currentMood = mood;
    var rec = document.getElementById('moodRecommendation');
    rec.textContent = moodRecommendations[mood];
    rec.classList.remove('hidden');
}

// =============================================
// MOVEMENT
// =============================================

function filterPractices(category, el) {
    document.querySelectorAll('#section-movement .cat-tab').forEach(function(t) { t.classList.remove('active'); });
    el.classList.add('active');
    document.querySelectorAll('.practice-card').forEach(function(card) {
        card.style.display = (category === 'all' || card.dataset.category === category) ? 'block' : 'none';
    });
}

function openPractice(practiceId) {
    var practice = practiceContent[practiceId];
    if (!practice) return;

    var stepsHtml = practice.steps.map(function(step, i) {
        return '<div class="practice-step"><div class="step-num">' + (i+1) + '</div><div class="step-content"><div class="step-header"><h4>' + step.name + '</h4><span class="step-duration">⏱️ ' + step.duration + '</span></div><p>' + step.desc + '</p></div></div>';
    }).join('');

    document.getElementById('practiceModalContent').innerHTML =
        '<div class="practice-modal-inner">' +
        '<h2>' + practice.title + '</h2>' +
        '<div class="practice-modal-meta"><span>⏱️ ' + practice.duration + '</span><span>🌿 ' + practice.level + '</span></div>' +
        '<p class="practice-modal-desc">' + practice.description + '</p>' +
        '<h3>Sequência</h3>' +
        '<div class="practice-steps">' + stepsHtml + '</div>' +
        '<button class="btn-primary" onclick="closePractice(); showToast(\'Prática iniciada! 🧘‍♀️\')">▶ Iniciar Prática</button>' +
        '</div>';

    document.getElementById('practiceModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closePractice() {
    document.getElementById('practiceModal').classList.add('hidden');
    document.body.style.overflow = '';
}

// =============================================
// NUTRITION
// =============================================

function renderMealPlan(diet) {
    var plan = mealPlans[diet] || mealPlans.omnivore;
    var container = document.getElementById('mealPlanContent');
    var html = '<div class="meal-plan">' + plan.map(function(meal) {
        return '<div class="meal-item"><div class="meal-time"><span class="meal-time-icon">' + meal.icon + '</span><span class="meal-time-label">' + meal.label + '</span><span class="meal-time-hour">' + meal.hour + '</span></div><div class="meal-name">' + meal.name + '</div><div class="meal-desc">' + meal.desc + '</div><div class="meal-macros">' + meal.macros.map(function(m) { return '<span class="macro-tag">' + m + '</span>'; }).join('') + '</div></div>';
    }).join('') + '</div>';
    container.innerHTML = html;
}

function filterMeals(diet, el) {
    document.querySelectorAll('#section-nutrition .cat-tab').forEach(function(t) { t.classList.remove('active'); });
    el.classList.add('active');
    renderMealPlan(diet === 'all' ? state.selectedDiet : diet);
}

function renderRecipes() {
    var container = document.getElementById('recipesGrid');
    container.innerHTML = recipes.map(function(r) {
        return '<div class="recipe-card"><span class="recipe-emoji">' + r.emoji + '</span><div class="recipe-info"><h4>' + r.name + '</h4><p>' + r.desc + '</p><div class="recipe-tags">' + r.tags.map(function(t) { return '<span class="recipe-tag">' + t + '</span>'; }).join('') + '</div></div></div>';
    }).join('');
}

function initWaterTracker() {
    var tracker = document.getElementById('waterTracker');
    tracker.innerHTML = '';
    for (var i = 0; i < 8; i++) {
        var cup = document.createElement('div');
        cup.className = 'water-cup';
        cup.innerHTML = '💧';
        cup.dataset.index = i;
        (function(idx) {
            cup.addEventListener('click', function() { toggleWater(idx); });
        })(i);
        tracker.appendChild(cup);
    }
}

function toggleWater(index) {
    var cups = document.querySelectorAll('.water-cup');
    var cup = cups[index];
    if (cup.classList.contains('filled')) {
        for (var i = index; i < 8; i++) { cups[i].classList.remove('filled'); }
        state.waterCount = index;
    } else {
        for (var i = 0; i <= index; i++) { cups[i].classList.add('filled'); }
        state.waterCount = index + 1;
    }
    document.getElementById('waterCount').textContent = state.waterCount + ' / 8 copos';
    if (state.waterCount === 8) { showToast('💧 Meta de hidratação atingida!'); }
}

// =============================================
// SCANBODY
// =============================================

function updateSliderValue(sliderId, displayId) {
    var val = document.getElementById(sliderId).value;
    document.getElementById(displayId).textContent = val;
}

function selectCyclePhase(el, phase) {
    document.querySelectorAll('.cycle-phase').forEach(function(p) { p.classList.remove('selected'); });
    el.classList.add('selected');
    state.currentCyclePhase = phase;
    var rec = cycleRecommendations[phase];
    var recEl = document.getElementById('cycleRecommendation');
    recEl.innerHTML = '<strong>' + rec.title + '</strong><br>🧘‍♀️ <strong>Prática:</strong> ' + rec.practice + '<br>🥗 <strong>Nutrição:</strong> ' + rec.nutrition + '<br>⚡ <strong>Energia:</strong> ' + rec.energy + '<br>💫 <em>' + rec.affirmation + '</em>';
    recEl.classList.remove('hidden');
}

function saveScanBody() {
    var data = {
        date: new Date().toISOString(),
        weight: document.getElementById('scanWeight').value,
        waist: document.getElementById('scanWaist').value,
        hip: document.getElementById('scanHip').value,
        bust: document.getElementById('scanBust').value,
        stress: document.getElementById('scanStress').value,
        sleep: document.getElementById('scanSleep').value,
        energy: document.getElementById('scanEnergy').value,
        focus: document.getElementById('scanFocus').value,
        mindBody: document.getElementById('scanMindBody').value,
        gratitude1: document.getElementById('gratitude1').value,
        gratitude2: document.getElementById('gratitude2').value,
        gratitude3: document.getElementById('gratitude3').value,
        observations: document.getElementById('scanObservations').value
    };
    state.scanBodyHistory.push(data);
    localStorage.setItem('sw_scanbody', JSON.stringify(state.scanBodyHistory));
    updateProgressBars(data);
    showToast('✅ Registro salvo com sucesso!');
}

function updateProgressBars(data) {
    var stressVal = parseInt(data.stress);
    var sleepVal = parseInt(data.sleep);
    var energyVal = parseInt(data.energy);
    var focusVal = parseInt(data.focus);
    document.querySelector('.stress-bar').style.width = (stressVal * 10) + '%';
    document.querySelector('.sleep-bar').style.width = (sleepVal * 10) + '%';
    document.querySelector('.energy-bar').style.width = (energyVal * 10) + '%';
    document.querySelector('.focus-bar').style.width = (focusVal * 10) + '%';
    document.getElementById('avgStress').textContent = stressVal.toFixed(1);
    document.getElementById('avgSleep').textContent = sleepVal.toFixed(1);
    document.getElementById('avgEnergy').textContent = energyVal.toFixed(1);
    document.getElementById('avgFocus').textContent = focusVal.toFixed(1);
}

// =============================================
// MARKETPLACE
// =============================================

function filterMarketplace(category, el) {
    document.querySelectorAll('#section-marketplace .cat-tab').forEach(function(t) { t.classList.remove('active'); });
    el.classList.add('active');
    document.querySelectorAll('.partner-card').forEach(function(card) {
        card.style.display = (category === 'all' || card.dataset.category === category) ? 'block' : 'none';
    });
}

function openPartner(partner) {
    var partnerUrls = {
        mundoverde: 'https://www.mundoverde.com.br',
        yogini: 'https://www.yogini.com.br',
        trackfield: 'https://www.tracknfield.com.br',
        soulwake: '#', aromas: '#', mindful: '#'
    };
    showToast('Abrindo parceiro Soul Wake... 🌿');
    setTimeout(function() {
        if (partnerUrls[partner] && partnerUrls[partner] !== '#') {
            window.open(partnerUrls[partner], '_blank');
        }
    }, 500);
}

// =============================================
// UTILS
// =============================================

function showToast(message) {
    var toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.remove('hidden');
    setTimeout(function() { toast.classList.add('hidden'); }, 3000);
}

// Inject modal styles
var modalStyles = document.createElement('style');
modalStyles.textContent = '.practice-modal-inner h2{font-family:"Playfair Display",serif;font-size:1.4rem;color:#8B2E1A;margin-bottom:10px}.practice-modal-meta{display:flex;gap:12px;margin-bottom:14px;font-size:.85rem;color:#9E7B6B}.practice-modal-desc{font-size:.9rem;color:#6B4C3B;line-height:1.6;margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid #E8D5C4}.practice-modal-inner h3{font-family:"Playfair Display",serif;font-size:1rem;color:#8B2E1A;margin-bottom:14px}.practice-steps{display:flex;flex-direction:column;gap:12px;margin-bottom:20px}.practice-step{display:flex;gap:12px;align-items:flex-start;background:#F5EDE0;border-radius:12px;padding:12px}.step-num{width:28px;height:28px;background:#8B2E1A;color:white;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.8rem;font-weight:700;flex-shrink:0}.step-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px}.step-header h4{font-size:.9rem;color:#8B2E1A}.step-duration{font-size:.75rem;color:#9E7B6B}.step-content p{font-size:.82rem;color:#6B4C3B;line-height:1.5}';
document.head.appendChild(modalStyles);

// =============================================
// INIT
// =============================================

window.addEventListener('DOMContentLoaded', function() {
    // Onboarding stress range
    var stressRange = document.getElementById('stressLevel');
    if (stressRange) {
        stressRange.addEventListener('input', function() {
            document.getElementById('stressValue').textContent = this.value + '/10';
        });
    }

    // Check if already onboarded
    if (localStorage.getItem('sw_onboarded') === 'true') {
        document.getElementById('onboardingOverlay').classList.add('hidden');
        document.getElementById('mainApp').classList.remove('hidden');
        initApp();
    }

    // Load saved scan body
    var savedScan = localStorage.getItem('sw_scanbody');
    if (savedScan) {
        try {
            state.scanBodyHistory = JSON.parse(savedScan);
            if (state.scanBodyHistory.length > 0) {
                updateProgressBars(state.scanBodyHistory[state.scanBodyHistory.length - 1]);
            }
        } catch(e) {}
    }
});
