/* Configuração do Rinópolis de Olho.
   Com supabaseUrl e supabaseChave preenchidos, o site público guarda as marcações no banco (todo mundo vê).
   Vazios, o site funciona em modo de demonstração (cada um vê só o que marcou). */
window.CONFIG = {
  supabaseUrl: '',   // "Project URL" do Supabase, ex.: https://abcdefgh.supabase.co
  supabaseChave: '', // chave "anon" ou "publishable" do Supabase (é pública, pode ficar no site)
  contato: '',       // e-mail para pedidos de remoção (LGPD)
  link: ''           // endereço do mapa, usado nas mensagens de WhatsApp e no boletim
};
