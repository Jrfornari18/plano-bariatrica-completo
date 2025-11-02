// UI para Receitas

document.addEventListener('DOMContentLoaded', () => {
    const recipesBtn = document.getElementById('recipesBtn');
    if (recipesBtn) {
        recipesBtn.addEventListener('click', showRecipesModal);
    }
});

function showRecipesModal() {
    // Criar modal
    const modal = document.createElement('div');
    modal.className = 'recipes-modal';
    modal.innerHTML = `
        <div class="recipes-modal-content">
            <div class="recipes-modal-header">
                <h2>📖 Receitas Saudáveis</h2>
                <button class="close-modal" onclick="closeRecipesModal()">&times;</button>
            </div>
            
            <div class="recipes-search">
                <input type="text" id="recipeSearch" placeholder="Buscar receita...">
            </div>
            
            <div class="recipes-tabs">
                <button class="recipe-tab active" data-category="cafeDaManha">Café da Manhã</button>
                <button class="recipe-tab" data-category="almoco">Almoço/Jantar</button>
                <button class="recipe-tab" data-category="lanches">Lanches</button>
                <button class="recipe-tab" data-category="posTreino">Pós-Treino</button>
                <button class="recipe-tab" data-category="sobremesas">Sobremesas</button>
            </div>
            
            <div class="recipes-container" id="recipesContainer">
                <!-- Receitas serão carregadas aqui -->
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Event listeners
    const tabs = modal.querySelectorAll('.recipe-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            loadRecipes(tab.dataset.category);
        });
    });
    
    const searchInput = modal.querySelector('#recipeSearch');
    searchInput.addEventListener('input', (e) => {
        if (e.target.value.trim()) {
            const results = searchRecipe(e.target.value);
            displayRecipes(results);
        } else {
            loadRecipes('cafeDaManha');
        }
    });
    
    // Carregar receitas iniciais
    loadRecipes('cafeDaManha');
    
    // Fechar ao clicar fora
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeRecipesModal();
        }
    });
}

function closeRecipesModal() {
    const modal = document.querySelector('.recipes-modal');
    if (modal) {
        modal.remove();
    }
}

function loadRecipes(category) {
    const recipes = getRecipesByCategory(category);
    displayRecipes(recipes);
}

function displayRecipes(recipes) {
    const container = document.getElementById('recipesContainer');
    
    if (recipes.length === 0) {
        container.innerHTML = '<p class="no-recipes">Nenhuma receita encontrada.</p>';
        return;
    }
    
    container.innerHTML = recipes.map(recipe => `
        <div class="recipe-card">
            <div class="recipe-header">
                <h3>${recipe.name}</h3>
                <span class="recipe-category">${recipe.category}</span>
            </div>
            
            <div class="recipe-meta">
                <span>⏱️ ${recipe.time}</span>
                <span>🍽️ ${recipe.servings} ${typeof recipe.servings === 'number' && recipe.servings === 1 ? 'porção' : 'porções'}</span>
            </div>
            
            <div class="recipe-macros">
                <div class="macro-item">
                    <span class="macro-label">Proteína</span>
                    <span class="macro-value">${recipe.macros.protein}</span>
                </div>
                <div class="macro-item">
                    <span class="macro-label">Carbs</span>
                    <span class="macro-value">${recipe.macros.carbs}</span>
                </div>
                <div class="macro-item">
                    <span class="macro-label">Gordura</span>
                    <span class="macro-value">${recipe.macros.fat}</span>
                </div>
                <div class="macro-item">
                    <span class="macro-label">Calorias</span>
                    <span class="macro-value">${recipe.macros.calories}</span>
                </div>
            </div>
            
            <div class="recipe-section">
                <h4>Ingredientes:</h4>
                <ul class="recipe-list">
                    ${recipe.ingredients.map(ing => `<li>${ing}</li>`).join('')}
                </ul>
            </div>
            
            <div class="recipe-section">
                <h4>Modo de Preparo:</h4>
                <ol class="recipe-steps">
                    ${recipe.instructions.map(step => `<li>${step}</li>`).join('')}
                </ol>
            </div>
            
            ${recipe.tips ? `
                <div class="recipe-tips">
                    <strong>💡 Dica:</strong> ${recipe.tips}
                </div>
            ` : ''}
        </div>
    `).join('');
}

// Fechar com ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeRecipesModal();
    }
});

