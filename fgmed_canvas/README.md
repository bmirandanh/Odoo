## FgmedCanvasContent - (fgmed.canvas.content)
Esta classe é responsável por organizar os conteúdos disponíveis no Canvas. Ela possui os seguintes campos:

### Campos
| Campo | Descrição |
|-------|-----------|
| name | Nome do conteúdo |
| canvas_id | Id do conteúdo no Canvas - id |
| canvas_secode | Código de inscrição - self_enrollment_code |
| unique | Código identificador do conteúdo no Canvas - uuid |
| description | Descrição do conteúdo |
| total_time | Duração total do conteúdo |
| custom_title | Título estilizado do conteúdo |
| thumbnail | Thumbnail do conteúdo |
| content_type | Tipo de conteúdo |
| author_ids | Autores |


## FgmedCanvasUsers - (fgmed.canvas.users)
Esta classe contém uma lista de usuários do Canvas e possui os seguintes campos:

### Campos
| Campo | Descrição |
|-------|-----------|
| user_id | ID do usuário |
| user_uuid | Hash do Usuário |


## FgmedCanvasContentType - (fgmed.canvas.content.type)
Esta classe permite categorizar por tipo os conteúdos do Canvas e possui apenas o campo a seguir:

### Campos
| Campo | Descrição |
|-------|-----------|
| name | Nome |


## FgmedCanvasAuthor - (fgmed.canvas.authors)
Esta classe permite administrar autores dos conteúdos do Canvas e possui os seguintes campos:

### Campos
| Campo | Descrição |
|-------|-----------|
| name | Nome |
| content_ids | Conteúdos do autor |


## FgmedCanvasContentViews - (fgmed.canvas.content.views)
Esta classe permite administrar visualizações dos conteúdos e possui os seguintes campos:

### Campos
| Campo | Descrição |
|-------|-----------|
| cv_content_id | Curso |
| cv_user_id | Usuário |


## FgmedCanvasContentInteraction - (fgmed.canvas.content.interactions)
Esta classe permite administrar interações nos conteúdos do Canvas e possui os seguintes campos:

### Campos
| Campo | Descrição |
|-------|-----------|
| cv_content_id | Curso |
| cv_user_id | Usuário |
| type | Tipo de interação |


## FgmedCanvasContentTime - (fgmed.canvas.content.times)
Esta classe registra o tempo utilizado em um recurso de acordo com cada usuário e possui os seguintes campos:

### Campos
| Campo | Descrição |
|-------|-----------|
| spent_time | Tempo consumido |
| cv_content_id | Curso |
| cv_user_id | Usuário |


## FgmedCanvasContentTags - (fgmed.canvas.content.tags)
Esta classe permite atribuir tags aos conteúdos e possui os seguintes campos:

### Campos
| Campo | Descrição |
|-------|-----------|
| name | Nome da tag |
| parent_path |  |
| parent_id | Tags superiores |
| child_ids | Subtags |


## FgmedCanvasEspecialidades - (fgmed.canvas.courses)
Esta classe representa as especialidades disponíveis aos assinantes.

### Campos
| Campo | Descrição |
|-------|-----------|
| name | Nome |
| image | Imagem |
| disciplina_ids | Disciplinas relacionadas |


## FgmedCanvasDisciplinas - (fgmed.canvas.modules)
Esta classe representa as disciplinas das especialidades disponíveis para os assinantes.

### Campos
| Campo | Descrição |
|-------|-----------|
| name | Nome |
| image | Imagem |
| especialidade_ids | Especialidades relacionadas |
