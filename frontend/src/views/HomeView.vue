<template>
  <div class="flex flex-col items-center justify-center h-screen bg-gray-100">
    <header class="text-center mb-8">
      <h1 class="text-4xl font-bold text-gray-800">Archestra</h1>
      <p class="text-lg text-gray-600">Skonfiguruj swoje mieszkanie</p>
    </header>

    <main>
      <RouterLink
        to="/preferences"
        class="px-6 py-3 bg-blue-500 text-white rounded-lg shadow hover:bg-blue-600 transition duration-200">
        Zacznij
      </RouterLink>
    </main>
  </div>
</template>