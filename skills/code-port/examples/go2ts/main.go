package main

import (
	"fmt"
	"io"
	"net/http"
	"sync"
)

type Fetcher interface {
	Fetch(url string) (string, error)
}

type httpFetcher struct{}

func (httpFetcher) Fetch(url string) (string, error) {
	resp, err := http.Get(url)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}
	return string(body), nil
}

type Result struct {
	URL   string
	Body  string
	Err   error
}

func fetchAll(f Fetcher, urls []string) []Result {
	results := make([]Result, len(urls))
	var wg sync.WaitGroup
	for i, u := range urls {
		wg.Add(1)
		go func(idx int, url string) {
			defer wg.Done()
			body, err := f.Fetch(url)
			results[idx] = Result{URL: url, Body: body, Err: err}
		}(i, u)
	}
	wg.Wait()
	return results
}

func main() {
	urls := []string{"https://example.com", "https://example.org"}
	res := fetchAll(httpFetcher{}, urls)
	for _, r := range res {
		if r.Err != nil {
			fmt.Printf("%s: error: %v\n", r.URL, r.Err)
			continue
		}
		fmt.Printf("%s: %d bytes\n", r.URL, len(r.Body))
	}
}
