import { api } from "./lib/axios"

function App() {

  const handleFileUpload = async (event: { target: { files: File[] | null } }) => {
    const file = event.target.files?.[0]
    if (!file) return

    const chunkSize = 1024 * 1024 // 1MB
    const totalChunks = Math.ceil(file.size / chunkSize)

    for (let i = 0; i < totalChunks; i++) {
      const start = i * chunkSize
      const end = Math.min(start + chunkSize, file.size)
      const chunk = file.slice(start, end)

      console.log("chunk.size >>>> ", chunk.size)

      // Upload the chunk to your server
      await uploadChunk(chunk, i, totalChunks, file.name)
    }
    const formData = new FormData()
    formData.append("total_chunks", totalChunks.toString());
    formData.append("file_name", file.name);
    
    // try {
    //   const response = await api.put('/api/upload/', formData, { headers: {'Content-Type': 'multipart/form-data'} })

    //   if (response.status !== 200) {
    //     throw new Error(`Could not merge chunks`)
    //   }


    // } catch (error) {

    // }
  }
  
  const uploadChunk = async (chunk: Blob, chunkIndex: number, totalChunks: number, fileName: string) => {
    const formData = new FormData()
    formData.append("file", chunk);
    formData.append("chunk_number", chunkIndex.toString());
    formData.append("total_chunks", totalChunks.toString());
    formData.append("file_name", fileName);

    try {
      const response = await api.post('/api/upload/', formData, { headers: {'Content-Type': 'multipart/form-data'} })
      

      if (response.status !== 200 && response.status !== 202) {
        throw new Error(`Chunk ${chunkIndex} upload failed`)
      }

      console.log(`Chunk ${chunkIndex} uploaded successfully`)
    } catch (error) {
      console.error(error)
    }
  }
  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const fileInput = event.currentTarget.elements.namedItem('file') as HTMLInputElement
    if (fileInput && fileInput.files) {
      const file = fileInput.files[0]
      if (file) {
        handleFileUpload({ target: { files: [file] } })
      }
    }
  }

  return (
    <div>
      <h1 className="font-bold h-32 flex-1">file by chunks test</h1>

      <form onSubmit={handleSubmit} className="flex gap-4 items-center justify-center">
        <label htmlFor="file" className="block p-2 bg-amber-300 cursor-pointer border-2 rounded-md text-sm font-medium text-gray-900 dark:text-white">Select file</label>
        <input className="sr-only" type="file" name="file" id="file" />
        <button type="submit">Upload</button>
      </form>
      
    </div>
  )
}

export default App
