import { useEffect, useMemo, useState } from 'react'
import { createFileRoute } from '@tanstack/react-router'
import { blink } from '@/blink/client'
import { BlinkClientBoundary } from '@/components/BlinkClientBoundary'
import { Timetable } from '@/components/Timetable'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { toast } from 'sonner'
import { Download, FileImage, FileText, GraduationCap, LogIn, Search, ShieldCheck, Trash2, Upload, X } from 'lucide-react'

type Resource = {
  id: string
  userId: string
  title: string
  description?: string
  category: string
  level?: string
  fileUrl: string
  fileName: string
  fileType: string
  authorName: string
  createdAt: string
}

const OWNER_ID = '5NxpDGYNK9SSFukg9j2lDlKGQt33'
const OWNER_NAME = 'KODJONE Kodjo'
const OWNER_PHONE = '+228 93 15 01 78'
const categories = ['Concours', 'Mathématiques', 'Examens', 'Cours', 'Images']
const demoResources: Resource[] = [
  { id: 'demo-1', userId: OWNER_ID, title: 'Préparation BAC 2025 — Mathématiques', description: 'Sujets et corrigés pour bien se préparer.', category: 'Examens', level: 'Lycée', fileUrl: '#', fileName: 'preparation-bac-maths.pdf', fileType: 'pdf', authorName: OWNER_NAME, createdAt: '2025-02-18' },
  { id: 'demo-2', userId: OWNER_ID, title: 'Guide concours ENA Togo', description: 'Ressources utiles pour les candidats.', category: 'Concours', level: 'Tous niveaux', fileUrl: '#', fileName: 'guide-concours-ena.pdf', fileType: 'pdf', authorName: OWNER_NAME, createdAt: '2025-02-11' },
  { id: 'demo-3', userId: OWNER_ID, title: 'Formules essentielles de géométrie', description: 'Une fiche visuelle à garder sous la main.', category: 'Mathématiques', level: 'Collège', fileUrl: '#', fileName: 'formules-geometrie.png', fileType: 'image', authorName: OWNER_NAME, createdAt: '2025-01-29' },
]

export const Route = createFileRoute('/')({
  head: () => ({ meta: [{ title: 'TogoEdu Hub · Ressources éducatives du Togo' }, { name: 'description', content: 'Téléchargez et partagez des ressources éducatives togolaises.' }] }),
  component: () => <BlinkClientBoundary fallback={<PageShell resources={demoResources} />}><TogoEduHub /></BlinkClientBoundary>,
})

function TogoEduHub() {
  const [resources, setResources] = useState<Resource[]>(demoResources)
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('Tous')
  const [user, setUser] = useState<{ id: string; email?: string; displayName?: string } | null>(null)
  const [isOwner, setIsOwner] = useState(false)
  const [showUpload, setShowUpload] = useState(false)

  useEffect(() => {
    const unsubscribe = blink.auth.onAuthStateChanged(async (state) => {
      const currentUser = state.user as typeof user
      setUser(currentUser)
      setIsOwner(currentUser?.id === OWNER_ID)
      if (!state.isLoading && currentUser) {
        try {
          const rows = await blink.db.table<Resource>('resources').list({ orderBy: { createdAt: 'desc' } })
          setResources(rows.length ? rows : demoResources)
        } catch (error) { toast.error(error instanceof Error ? error.message : 'Impossible de charger les ressources.') }
      }
    })
    return unsubscribe
  }, [])

  const filtered = useMemo(() => resources.filter((resource) => {
    const matchesQuery = `${resource.title} ${resource.description ?? ''} ${resource.category}`.toLowerCase().includes(query.toLowerCase())
    return matchesQuery && (category === 'Tous' || resource.category === category)
  }), [resources, query, category])

  const removeResource = async (id: string) => {
    try { await blink.db.table<Resource>('resources').delete(id); setResources((current) => current.filter((item) => item.id !== id)); toast.success('Document retiré de la bibliothèque.') }
    catch (error) { toast.error(error instanceof Error ? error.message : 'Suppression impossible.') }
  }

  return <PageShell resources={filtered} query={query} setQuery={setQuery} category={category} setCategory={setCategory} user={user} isOwner={isOwner} showUpload={showUpload} setShowUpload={setShowUpload} onRemove={removeResource} onLogin={() => blink.auth.login()} />
}

function PageShell({ resources, query = '', setQuery = () => undefined, category = 'Tous', setCategory = () => undefined, user = null, isOwner = false, showUpload = false, setShowUpload = () => undefined, onRemove = () => undefined, onLogin = () => undefined }: { resources: Resource[]; query?: string; setQuery?: (value: string) => void; category?: string; setCategory?: (value: string) => void; user?: { id: string; email?: string; displayName?: string } | null; isOwner?: boolean; showUpload?: boolean; setShowUpload?: (value: boolean) => void; onRemove?: (id: string) => void; onLogin?: () => void }) {
  return <div className="min-h-dvh bg-background text-foreground">
    <header className="border-b border-border/70 bg-sidebar text-sidebar-foreground"><div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-4 lg:px-8"><a href="/" className="flex items-center gap-3"><span className="grid size-10 place-items-center rounded-xl bg-sidebar-primary text-sidebar-primary-foreground shadow-md"><GraduationCap className="size-6" /></span><span><strong className="block font-serif text-lg">TogoEdu Hub</strong><small className="text-xs text-sidebar-foreground/70">Le savoir au service du Togo</small></span></a><div className="flex items-center gap-2">{isOwner && <Button onClick={() => setShowUpload(true)} className="bg-sidebar-primary text-sidebar-primary-foreground hover:bg-sidebar-primary/90"><Upload className="size-4" />Publier</Button>}{user ? <span className="hidden text-xs text-sidebar-foreground/70 sm:block">{user.displayName || user.email}</span> : <Button variant="outline" onClick={onLogin} className="border-sidebar-foreground/30 bg-transparent text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"><LogIn className="size-4" />Connexion</Button>}</div></div></header>
    <main><section className="relative overflow-hidden bg-sidebar px-5 pb-20 pt-14 text-sidebar-foreground lg:px-8 lg:pb-28"><div className="absolute -right-24 -top-32 size-96 rounded-full bg-sidebar-primary/15 blur-3xl" /><div className="relative mx-auto max-w-7xl"><p className="mb-5 font-mono text-xs uppercase tracking-[0.24em] text-sidebar-primary">Ressources éducatives togolaises</p><h1 className="max-w-3xl font-serif text-4xl leading-tight sm:text-6xl">Apprendre, réussir,<br /><span className="text-sidebar-primary">construire le Togo.</span></h1><p className="mt-6 max-w-xl text-base leading-7 text-sidebar-foreground/75">Une bibliothèque ouverte de cours, concours, examens et images pour les élèves, étudiants et enseignants du Togo.</p><div className="mt-8 flex flex-wrap items-center gap-3 text-sm text-sidebar-foreground/70"><span className="flex items-center gap-2"><ShieldCheck className="size-4 text-sidebar-primary" />Ressources vérifiées</span><span className="h-1 w-1 rounded-full bg-sidebar-primary" /><span>Créé par {OWNER_NAME}</span></div></div></section>
      <section className="mx-auto max-w-7xl px-5 py-10 lg:px-8"><div className="-mt-16 rounded-2xl border border-border bg-card p-3 shadow-lg sm:p-4"><div className="flex items-center gap-3"><Search className="ml-2 size-5 text-muted-foreground" /><Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Rechercher un cours, un concours, un examen..." className="border-0 bg-transparent shadow-none focus-visible:ring-0" /></div></div><div className="mt-8 flex gap-2 overflow-x-auto pb-2">{['Tous', ...categories].map((item) => <button key={item} onClick={() => setCategory(item)} className={`whitespace-nowrap rounded-full px-4 py-2 text-sm transition-all ${category === item ? 'bg-primary text-primary-foreground shadow-md' : 'bg-card text-muted-foreground hover:bg-secondary'}`}>{item}</button>)}</div><div className="mt-8 flex items-end justify-between"><div><p className="font-mono text-xs uppercase tracking-[0.18em] text-primary">Bibliothèque</p><h2 className="mt-2 font-serif text-3xl">Ressources populaires</h2></div><span className="text-sm text-muted-foreground">{resources.length} documents</span></div><div className="mt-6 grid gap-5 md:grid-cols-2 lg:grid-cols-3">{resources.map((resource) => <ResourceCard key={resource.id} resource={resource} canRemove={isOwner && resource.id.startsWith('demo-') === false} onRemove={onRemove} />)}</div>{resources.length === 0 && <div className="rounded-2xl border border-dashed border-border py-16 text-center text-muted-foreground">Aucune ressource ne correspond à votre recherche.</div>}</section>
      <Timetable />
    </main>
    <footer className="border-t border-border bg-secondary/50 px-5 py-10 lg:px-8"><div className="mx-auto flex max-w-7xl flex-col gap-5 text-sm text-muted-foreground sm:flex-row sm:items-end sm:justify-between"><div><p className="font-serif text-lg text-foreground">TogoEdu Hub</p><p className="mt-1">Une initiative de {OWNER_NAME}, Prof de Maths</p><p className="mt-1 font-mono text-xs">Contact : {OWNER_PHONE}</p></div><p className="max-w-xs text-left sm:text-right">Chaque document partagé porte le crédit de son créateur et contribue à la réussite de notre communauté.</p></div></footer>
    {showUpload && <UploadDialog onClose={() => setShowUpload(false)} />}
  </div>
}

function ResourceCard({ resource, canRemove, onRemove }: { resource: Resource; canRemove: boolean; onRemove: (id: string) => void }) { const Icon = resource.fileType === 'image' ? FileImage : FileText; return <Card className="group overflow-hidden border-border/80 transition-all hover:-translate-y-1 hover:shadow-lg"><CardHeader className="pb-3"><div className="flex items-start justify-between"><span className="rounded-full bg-secondary px-3 py-1 text-xs font-medium text-secondary-foreground">{resource.category}</span><Icon className="size-5 text-primary" /></div><CardTitle className="pt-2 font-serif text-xl leading-snug">{resource.title}</CardTitle><CardDescription>{resource.description}</CardDescription></CardHeader><CardContent><div className="flex items-center justify-between border-t border-border pt-4 text-xs text-muted-foreground"><span>{resource.level || 'Tous niveaux'}</span><span>{resource.authorName}</span></div><div className="mt-4 flex gap-2"><a href={resource.fileUrl === '#' ? undefined : resource.fileUrl} target="_blank" rel="noreferrer" download={resource.fileName} onClick={(event) => resource.fileUrl === '#' && event.preventDefault()} className="inline-flex h-9 flex-1 items-center justify-center gap-2 rounded-md bg-primary px-3 text-sm font-medium text-primary-foreground transition hover:bg-primary/90"><Download className="size-4" />Télécharger</a>{canRemove && <Button variant="outline" size="icon" aria-label="Retirer" onClick={() => onRemove(resource.id)}><Trash2 className="size-4" /></Button>}</div></CardContent></Card> }

function UploadDialog({ onClose }: { onClose: () => void }) { const [title, setTitle] = useState(''); const [category, setCategory] = useState(categories[0]); const [file, setFile] = useState<File | null>(null); const [busy, setBusy] = useState(false); const submit = async () => { if (!title || !file) { toast.error('Ajoutez un titre et un fichier.'); return }; setBusy(true); try { const extension = file.name.split('.').pop() || 'bin'; const upload = await blink.storage.upload(file, `resources/${Date.now()}-${crypto.randomUUID()}.${extension}`); await blink.db.table<Resource>('resources').create({ userId: OWNER_ID, title, category, description: 'Ressource publiée par TogoEdu Hub.', level: 'Tous niveaux', fileUrl: upload.publicUrl, fileName: file.name, fileType: file.type.startsWith('image/') ? 'image' : 'pdf', authorName: OWNER_NAME }); toast.success('Ressource publiée avec succès.'); onClose(); window.location.reload() } catch (error) { toast.error(error instanceof Error ? error.message : 'Publication impossible.') } finally { setBusy(false) } }; return <div className="fixed inset-0 z-50 grid place-items-center bg-foreground/40 p-4" role="dialog" aria-modal="true"><Card className="w-full max-w-lg shadow-lg"><CardHeader><div className="flex items-center justify-between"><div><CardTitle className="font-serif text-2xl">Publier une ressource</CardTitle><CardDescription>Seul le propriétaire peut publier.</CardDescription></div><Button variant="ghost" size="icon" onClick={onClose} aria-label="Fermer"><X className="size-5" /></Button></div></CardHeader><CardContent className="space-y-4"><Input placeholder="Titre du document" value={title} onChange={(event) => setTitle(event.target.value)} /><select value={category} onChange={(event) => setCategory(event.target.value)} className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm"><option>{categories[0]}</option>{categories.slice(1).map((item) => <option key={item}>{item}</option>)}</select><label className="flex cursor-pointer flex-col items-center gap-2 rounded-xl border border-dashed border-primary/40 bg-secondary/40 px-5 py-8 text-center text-sm"><Upload className="size-6 text-primary" /><span>{file ? file.name : 'Choisir un PDF, une image ou un document'}</span><input type="file" accept=".pdf,.doc,.docx,.png,.jpg,.jpeg" className="sr-only" onChange={(event) => setFile(event.target.files?.[0] || null)} /></label><Button className="w-full" onClick={submit} disabled={busy}>{busy ? 'Publication...' : 'Publier la ressource'}</Button></CardContent></Card></div> }
