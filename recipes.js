// Receitas Saudáveis para o Plano Pós-Bariátrica

const RECIPES = {
    cafeDaManha: [
        {
            name: 'Omelete Proteica de Claras',
            category: 'Café da Manhã',
            time: '10 min',
            servings: 1,
            macros: { protein: '28g', carbs: '5g', fat: '8g', calories: '200 kcal' },
            ingredients: [
                '3 claras de ovo',
                '1 ovo inteiro',
                '30g de queijo cottage',
                '1 tomate picado',
                'Espinafre à vontade',
                'Sal e pimenta a gosto',
                'Spray antiaderente'
            ],
            instructions: [
                'Bata os ovos com as claras em uma tigela',
                'Adicione o queijo cottage e misture bem',
                'Aqueça uma frigideira antiaderente com spray',
                'Despeje a mistura e adicione tomate e espinafre',
                'Cozinhe em fogo baixo até firmar',
                'Dobre ao meio e sirva imediatamente'
            ],
            tips: 'Pode adicionar cogumelos, pimentão ou cebola para mais sabor e nutrientes.'
        },
        {
            name: 'Panqueca de Banana e Aveia Proteica',
            category: 'Café da Manhã',
            time: '15 min',
            servings: 1,
            macros: { protein: '25g', carbs: '35g', fat: '6g', calories: '290 kcal' },
            ingredients: [
                '1 banana madura',
                '2 ovos',
                '30g de aveia em flocos',
                '1 scoop de whey protein (baunilha)',
                '1 colher de chá de canela',
                'Spray antiaderente'
            ],
            instructions: [
                'Amasse a banana em uma tigela',
                'Adicione os ovos e bata bem',
                'Misture a aveia, whey e canela',
                'Deixe descansar por 2 minutos',
                'Aqueça frigideira com spray',
                'Faça panquecas pequenas (fáceis de virar)',
                'Cozinhe 2-3 min cada lado'
            ],
            tips: 'Sirva com frutas vermelhas ou um fio de mel (opcional).'
        },
        {
            name: 'Overnight Oats Proteico',
            category: 'Café da Manhã',
            time: '5 min + 8h geladeira',
            servings: 1,
            macros: { protein: '30g', carbs: '40g', fat: '8g', calories: '350 kcal' },
            ingredients: [
                '40g de aveia em flocos',
                '1 scoop de whey protein',
                '200ml de leite desnatado',
                '1 colher de sopa de chia',
                '1/2 banana fatiada',
                'Canela a gosto'
            ],
            instructions: [
                'Em um pote, misture aveia, whey e chia',
                'Adicione o leite e misture bem',
                'Coloque a banana fatiada por cima',
                'Polvilhe canela',
                'Tampe e leve à geladeira por 8h (ou overnight)',
                'Pela manhã, misture e está pronto para comer'
            ],
            tips: 'Prepare na noite anterior para economizar tempo pela manhã.'
        }
    ],
    
    almoco: [
        {
            name: 'Frango Grelhado com Legumes Assados',
            category: 'Almoço/Jantar',
            time: '35 min',
            servings: 1,
            macros: { protein: '45g', carbs: '30g', fat: '10g', calories: '400 kcal' },
            ingredients: [
                '150g de peito de frango',
                '100g de batata doce em cubos',
                '1 abobrinha fatiada',
                '1 cenoura em rodelas',
                'Brócolis à vontade',
                '1 colher de sopa de azeite',
                'Alho, limão, ervas (alecrim, tomilho)',
                'Sal e pimenta'
            ],
            instructions: [
                'Tempere o frango com alho, limão, sal e pimenta',
                'Deixe marinar por 15 min',
                'Pré-aqueça o forno a 200°C',
                'Coloque os legumes em uma assadeira com azeite',
                'Tempere com sal, pimenta e ervas',
                'Asse por 25 min',
                'Grelhe o frango em frigideira (5-7 min cada lado)',
                'Sirva tudo junto'
            ],
            tips: 'Prepare em maior quantidade para ter marmitas prontas.'
        },
        {
            name: 'Salmão ao Forno com Aspargos',
            category: 'Almoço/Jantar',
            time: '25 min',
            servings: 1,
            macros: { protein: '40g', carbs: '15g', fat: '18g', calories: '380 kcal' },
            ingredients: [
                '150g de filé de salmão',
                '200g de aspargos',
                '1 colher de sopa de azeite',
                '1 limão (suco e raspas)',
                '2 dentes de alho picados',
                'Sal, pimenta e endro'
            ],
            instructions: [
                'Pré-aqueça o forno a 200°C',
                'Tempere o salmão com sal, pimenta, alho e endro',
                'Regue com suco de limão',
                'Coloque em uma assadeira forrada',
                'Disponha os aspargos ao redor',
                'Regue tudo com azeite',
                'Asse por 15-18 min',
                'Finalize com raspas de limão'
            ],
            tips: 'O salmão é rico em ômega-3, excelente para recuperação muscular.'
        },
        {
            name: 'Bowl de Carne Magra com Quinoa',
            category: 'Almoço/Jantar',
            time: '30 min',
            servings: 1,
            macros: { protein: '42g', carbs: '45g', fat: '12g', calories: '460 kcal' },
            ingredients: [
                '150g de patinho moído',
                '80g de quinoa cozida',
                'Folhas verdes (rúcula, alface)',
                '1 tomate picado',
                '1/2 abacate fatiado',
                '1 colher de sopa de azeite',
                'Limão, sal e pimenta'
            ],
            instructions: [
                'Cozinhe a quinoa conforme embalagem',
                'Tempere a carne com sal, pimenta e alho',
                'Refogue a carne até dourar',
                'Monte o bowl: base de folhas verdes',
                'Adicione quinoa, carne, tomate e abacate',
                'Regue com azeite e limão',
                'Misture tudo na hora de comer'
            ],
            tips: 'Adicione grão-de-bico ou feijão preto para mais fibras.'
        }
    ],
    
    lanches: [
        {
            name: 'Pasta de Atum Proteica',
            category: 'Lanche',
            time: '5 min',
            servings: 1,
            macros: { protein: '25g', carbs: '8g', fat: '5g', calories: '180 kcal' },
            ingredients: [
                '1 lata de atum em água (drenado)',
                '2 colheres de sopa de queijo cottage',
                '1 colher de chá de mostarda',
                'Salsinha picada',
                'Sal e pimenta',
                'Palitos de cenoura e pepino'
            ],
            instructions: [
                'Escorra bem o atum',
                'Misture com cottage e mostarda',
                'Adicione salsinha, sal e pimenta',
                'Amasse com garfo até ficar cremoso',
                'Sirva com palitos de vegetais'
            ],
            tips: 'Pode comer com torradas integrais ou usar como recheio de wrap.'
        },
        {
            name: 'Energy Balls Proteicas',
            category: 'Lanche',
            time: '15 min',
            servings: '10 bolinhas',
            macros: { protein: '4g/unidade', carbs: '8g', fat: '5g', calories: '90 kcal' },
            ingredients: [
                '100g de tâmaras sem caroço',
                '50g de amêndoas',
                '30g de whey protein (chocolate)',
                '2 colheres de sopa de cacau em pó',
                '1 colher de sopa de pasta de amendoim',
                'Água conforme necessário'
            ],
            instructions: [
                'Processe as tâmaras e amêndoas no processador',
                'Adicione whey, cacau e pasta de amendoim',
                'Processe até formar uma massa',
                'Se necessário, adicione água aos poucos',
                'Faça bolinhas com as mãos',
                'Leve à geladeira por 1h',
                'Guarde em pote fechado'
            ],
            tips: 'Duram até 1 semana na geladeira. Ótimo pré-treino!'
        },
        {
            name: 'Iogurte Grego Turbinado',
            category: 'Lanche',
            time: '3 min',
            servings: 1,
            macros: { protein: '22g', carbs: '18g', fat: '6g', calories: '210 kcal' },
            ingredients: [
                '170g de iogurte grego natural 0%',
                '1 scoop de whey protein',
                '1 colher de sopa de chia',
                '50g de frutas vermelhas',
                '10g de granola sem açúcar'
            ],
            instructions: [
                'Coloque o iogurte em uma tigela',
                'Misture o whey até ficar homogêneo',
                'Adicione a chia',
                'Cubra com frutas vermelhas',
                'Finalize com granola'
            ],
            tips: 'Substitua frutas conforme preferência e disponibilidade.'
        }
    ],
    
    posTreino: [
        {
            name: 'Shake Pós-Treino Completo',
            category: 'Pós-Treino',
            time: '3 min',
            servings: 1,
            macros: { protein: '35g', carbs: '45g', fat: '5g', calories: '360 kcal' },
            ingredients: [
                '1 scoop de whey protein',
                '1 banana',
                '200ml de leite desnatado',
                '1 colher de sopa de aveia',
                '1 colher de chá de pasta de amendoim',
                'Gelo'
            ],
            instructions: [
                'Coloque todos os ingredientes no liquidificador',
                'Bata até ficar cremoso',
                'Adicione gelo se quiser mais gelado',
                'Beba imediatamente após o treino'
            ],
            tips: 'Consuma em até 30 min após o treino para melhor absorção.'
        },
        {
            name: 'Batata Doce com Frango Desfiado',
            category: 'Pós-Treino',
            time: '25 min',
            servings: 1,
            macros: { protein: '40g', carbs: '50g', fat: '8g', calories: '440 kcal' },
            ingredients: [
                '200g de batata doce',
                '120g de peito de frango cozido',
                '1 colher de sopa de requeijão light',
                'Cebolinha picada',
                'Sal e pimenta'
            ],
            instructions: [
                'Cozinhe a batata doce até ficar macia',
                'Desfie o frango',
                'Corte a batata ao meio',
                'Amasse levemente com garfo',
                'Cubra com frango desfiado',
                'Adicione requeijão e cebolinha',
                'Tempere a gosto'
            ],
            tips: 'Prepare o frango em maior quantidade para ter sempre pronto.'
        }
    ],
    
    sobremesas: [
        {
            name: 'Mousse Proteica de Chocolate',
            category: 'Sobremesa',
            time: '10 min + 2h geladeira',
            servings: 2,
            macros: { protein: '20g', carbs: '12g', fat: '4g', calories: '160 kcal' },
            ingredients: [
                '200g de iogurte grego 0%',
                '1 scoop de whey protein chocolate',
                '1 colher de sopa de cacau em pó',
                'Adoçante a gosto',
                '50ml de leite desnatado'
            ],
            instructions: [
                'Bata todos os ingredientes no liquidificador',
                'Ajuste consistência com leite se necessário',
                'Distribua em taças',
                'Leve à geladeira por 2h',
                'Decore com cacau em pó'
            ],
            tips: 'Pode adicionar frutas vermelhas por cima.'
        },
        {
            name: 'Brigadeiro Proteico Fit',
            category: 'Sobremesa',
            time: '15 min',
            servings: '12 unidades',
            macros: { protein: '3g/unidade', carbs: '5g', fat: '2g', calories: '50 kcal' },
            ingredients: [
                '1 lata de leite condensado zero açúcar',
                '2 scoops de whey protein chocolate',
                '2 colheres de sopa de cacau em pó',
                '1 colher de sopa de manteiga',
                'Cacau em pó para decorar'
            ],
            instructions: [
                'Misture todos os ingredientes em uma panela',
                'Cozinhe em fogo baixo mexendo sempre',
                'Quando desgrudar do fundo, está pronto',
                'Deixe esfriar',
                'Faça bolinhas e passe no cacau',
                'Guarde na geladeira'
            ],
            tips: 'Perfeito para quando bater vontade de doce!'
        }
    ]
};

// Função para filtrar receitas por categoria
function getRecipesByCategory(category) {
    return RECIPES[category] || [];
}

// Função para buscar receita por nome
function searchRecipe(searchTerm) {
    const allRecipes = [
        ...RECIPES.cafeDaManha,
        ...RECIPES.almoco,
        ...RECIPES.lanches,
        ...RECIPES.posTreino,
        ...RECIPES.sobremesas
    ];
    
    return allRecipes.filter(recipe => 
        recipe.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        recipe.category.toLowerCase().includes(searchTerm.toLowerCase())
    );
}

// Exportar para uso no app
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { RECIPES, getRecipesByCategory, searchRecipe };
}

